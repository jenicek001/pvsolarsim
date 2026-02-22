"""
Prague PV System: February 22, 2026 Production Prediction
==========================================================
Uses Visual Crossing live weather API to:
  1. Reconstruct yesterday (Feb 21) and validate against real observed data
  2. Predict today (Feb 22) production for the Prague 14.04 kWp system

Observed data for Feb 21:
  - Peak power ~3.5 kW between 12:00–14:00 CET
  - Rest of day: ~1 kW max

API key is read from $VISUAL_CROSSING_API_KEY (or .env in project root).
"""

import os
import sys
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import pytz

# Load .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    load_dotenv(_env_path)
except ImportError:
    pass

# Ensure pvsolarsim is importable when running from examples/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pvsolarsim import Location, PVSystem, calculate_power
from pvsolarsim.weather import VisualCrossingClient

# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────
LAT = 50.0807494
LON = 14.8594164
ALT = 220
TIMEZONE = "Europe/Prague"

MUNCHEN_COUNT = 16
MUNCHEN_WP = 450
MUNCHEN_EFF = 0.2037
MUNCHEN_TC = -0.0035
MUNCHEN_AREA = 2.108 * 1.048

CANADIAN_COUNT = 18
CANADIAN_WP = 380
CANADIAN_EFF = 0.205
CANADIAN_TC = -0.0037
CANADIAN_AREA = 1.765 * 1.048

TOTAL_WP = MUNCHEN_COUNT * MUNCHEN_WP + CANADIAN_COUNT * CANADIAN_WP
TOTAL_AREA = MUNCHEN_COUNT * MUNCHEN_AREA + CANADIAN_COUNT * CANADIAN_AREA
WEIGHTED_EFF = TOTAL_WP / (TOTAL_AREA * 1000)
WEIGHTED_TC = (
    MUNCHEN_COUNT * MUNCHEN_WP * MUNCHEN_TC
    + CANADIAN_COUNT * CANADIAN_WP * CANADIAN_TC
) / TOTAL_WP

TILT = 35.0
AZIMUTH = 202.0
INVERTER_EFF = 0.97

# Observed yesterday (user-reported)
YESTERDAY_OBSERVED = {
    "peak_kw": 3.5,
    "peak_hours": (12, 14),  # CET
    "bulk_max_kw": 1.0,
}

YESTERDAY = date(2026, 2, 21)
TODAY = date(2026, 2, 22)


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def bar(value, max_value=20.0, width=40) -> str:
    """ASCII bar chart, 0..max_value → 0..width chars."""
    filled = int(round(value / max_value * width))
    filled = max(0, min(filled, width))
    return "█" * filled


def sep(title="", char="═", width=90):
    if title:
        side = (width - len(title) - 2) // 2
        print(f"\n{char * side} {title} {char * side}\n")
    else:
        print(char * width)


def simulate_day(location: Location, system: PVSystem, weather_df: pd.DataFrame,
                 day: date) -> pd.DataFrame:
    """
    Run hourly calculate_power() for the given day using weather_df (UTC index).
    Passes actual GHI/DNI/DHI from VC directly – bypasses the cloud model so
    the irradiance used is exactly what was measured/forecast.
    Returns a DataFrame with local-time columns.
    """
    prague_tz = pytz.timezone(TIMEZONE)
    rows = []

    for hour in range(24):
        local_ts = datetime(day.year, day.month, day.day, hour, 0, 0,
                            tzinfo=prague_tz)
        utc_ts = local_ts.astimezone(pytz.UTC)

        # Find closest row in weather_df by UTC hour
        hour_idx = weather_df.index[weather_df.index.hour == utc_ts.hour]
        if len(hour_idx) == 0:
            continue
        w = weather_df.loc[hour_idx[0]]

        ghi = max(0.0, float(w.get("ghi", 0)))
        dni = max(0.0, float(w.get("dni", 0)))
        # Clip dhi to 0.01 minimum: Perez model divides by dhi and crashes on 0
        dhi = max(0.01, float(w.get("dhi", 0)))
        temp = float(w.get("temp_air", 5))
        wind = float(w.get("wind_speed", 2))
        cloud = float(w.get("cloud_cover", 50))

        # Pass measured irradiance directly – the model uses these instead of
        # computing its own clear-sky values, giving the most accurate result.
        result = calculate_power(
            location=location,
            system=system,
            timestamp=local_ts,
            ambient_temp=temp,
            wind_speed=wind,
            ghi=ghi,
            dni=dni,
            dhi=dhi,
            soiling_factor=0.97,
            inverter_efficiency=INVERTER_EFF,
        )

        pw_dc = 0.0 if np.isnan(result.power_w) else result.power_w / 1000.0
        pw_ac = 0.0 if np.isnan(result.power_ac_w) else result.power_ac_w / 1000.0

        rows.append({
            "hour_local": hour,
            "local_ts": local_ts,
            "temp_c": temp,
            "wind_ms": wind,
            "cloud_pct": cloud,
            "ghi_wm2": ghi,
            "poa_wm2": result.poa_irradiance,
            "solar_elev": result.solar_elevation,
            "cell_temp_c": result.cell_temperature,
            "dc_kw": pw_dc,
            "ac_kw": pw_ac,
        })

    return pd.DataFrame(rows)


def print_hourly_table(df: pd.DataFrame, observed: dict | None = None):
    """Print production-hour table, optionally with observed values column."""
    production = df[df["dc_kw"] > 0.05]
    if production.empty:
        print("  ⚠ No significant production (sun below horizon all day)")
        return

    has_obs = observed is not None
    if has_obs:
        hdr = f"{'Hour':<6} {'GHI':>7} {'POA':>7} {'DC kW':>8} {'AC kW':>8} {'Observed':>10}  {'Elev':>6} {'Tcell':>6}"
        print(hdr)
        print("─" * 72)
    else:
        hdr = f"{'Hour':<6} {'GHI':>7} {'POA':>7} {'DC kW':>8} {'AC kW':>8}  {'Elev':>6} {'Tcell':>6}  Bar"
        print(hdr)
        print("─" * 80)

    peak_obs = observed.get("peak_kw", 0) if has_obs else 0
    peak_hours = observed.get("peak_hours", (12, 14)) if has_obs else (12, 14)
    bulk_max = observed.get("bulk_max_kw", 1.0) if has_obs else 1.0

    for _, row in production.iterrows():
        h = int(row["hour_local"])
        ts_str = f"{h:02d}:00"

        # Determine observed estimate for this hour
        if has_obs:
            if peak_hours[0] <= h < peak_hours[1]:
                obs_str = f"~{peak_obs:.1f} kW ✓"
            elif row["dc_kw"] > 0.05:
                obs_str = f"~{bulk_max:.1f} kW"
            else:
                obs_str = "night"

            print(
                f"{ts_str:<6} {row['ghi_wm2']:>7.0f} {row['poa_wm2']:>7.0f} "
                f"{row['dc_kw']:>7.2f}  {row['ac_kw']:>7.2f}  "
                f"{obs_str:>14}  "
                f"{row['solar_elev']:>5.1f}° {row['cell_temp_c']:>5.1f}°C"
            )
        else:
            b = bar(row["dc_kw"], max_value=TOTAL_WP / 1000)
            print(
                f"{ts_str:<6} {row['ghi_wm2']:>7.0f} {row['poa_wm2']:>7.0f} "
                f"{row['dc_kw']:>7.2f}  {row['ac_kw']:>7.2f}  "
                f"{row['solar_elev']:>5.1f}° {row['cell_temp_c']:>5.1f}°C  {b}"
            )


def print_weather_summary(df_wx: pd.DataFrame, label: str, tz_name: str = "Europe/Prague"):
    """Print key weather stats over the daylight window."""
    prague_tz = pytz.timezone(tz_name)
    local_idx = df_wx.index.tz_convert(prague_tz)
    day_mask = (local_idx.hour >= 7) & (local_idx.hour <= 18)
    day = df_wx[day_mask]
    if day.empty:
        day = df_wx

    print(f"  {label}")
    print(f"    GHI (daylight):   min={day['ghi'].min():.0f}  max={day['ghi'].max():.0f}  "
          f"mean={day['ghi'].mean():.0f} W/m²")
    print(f"    Temperature:      min={day['temp_air'].min():.1f}  max={day['temp_air'].max():.1f}  "
          f"mean={day['temp_air'].mean():.1f} °C")
    print(f"    Cloud cover:      min={day['cloud_cover'].min():.0f}  max={day['cloud_cover'].max():.0f}  "
          f"mean={day['cloud_cover'].mean():.0f} %")
    print(f"    Wind speed:       mean={day['wind_speed'].mean():.1f} m/s")


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    api_key = os.getenv("VISUAL_CROSSING_API_KEY", "")
    if not api_key:
        print("ERROR: VISUAL_CROSSING_API_KEY not found in environment or .env")
        print("       Set it with: export VISUAL_CROSSING_API_KEY=<your_key>")
        sys.exit(1)

    sep("Prague 14.04 kWp – Feb 22, 2026 Prediction vs Feb 21 Reality")

    # ─ Build objects ─────────────────────────────────────────────────────────
    location = Location(latitude=LAT, longitude=LON, altitude=ALT, timezone=TIMEZONE)
    system = PVSystem(
        panel_area=TOTAL_AREA,
        panel_efficiency=WEIGHTED_EFF,
        tilt=TILT,
        azimuth=AZIMUTH,
        temp_coefficient=WEIGHTED_TC,
    )
    client = VisualCrossingClient(api_key=api_key)

    print(f"System:   {TOTAL_WP/1000:.2f} kWp  ({MUNCHEN_COUNT}× München 450W + {CANADIAN_COUNT}× Canadian 380W)")
    print(f"Location: {LAT:.4f}°N, {LON:.4f}°E, {ALT}m  ({TIMEZONE})")
    print(f"Panel:    {TILT}° tilt, {AZIMUTH}° azimuth (SSW), {WEIGHTED_EFF*100:.2f}% efficiency")

    # ─ Fetch weather ─────────────────────────────────────────────────────────
    sep("Fetching Weather Data from Visual Crossing", "─")
    print(f"  Fetching {YESTERDAY} (yesterday) …", end=" ", flush=True)
    wx_yesterday = client.read(LAT, LON, start=YESTERDAY, end=YESTERDAY)
    print(f"✅  {len(wx_yesterday)} records")

    print(f"  Fetching {TODAY}  (today)     …", end=" ", flush=True)
    wx_today = client.read(LAT, LON, start=TODAY, end=TODAY)
    print(f"✅  {len(wx_today)} records\n")

    print_weather_summary(wx_yesterday, f"Feb 21 (yesterday)")
    print()
    print_weather_summary(wx_today, f"Feb 22 (today)")

    # ─ Simulate ──────────────────────────────────────────────────────────────
    sep("Feb 21, 2026 – Simulation vs Your Observed Data", "─")

    sim_yesterday = simulate_day(location, system, wx_yesterday, YESTERDAY)

    daily_dc_y = sim_yesterday["dc_kw"].sum()
    daily_ac_y = sim_yesterday["ac_kw"].sum()
    peak_dc_y = sim_yesterday["dc_kw"].max()
    peak_hour_y = sim_yesterday.loc[sim_yesterday["dc_kw"].idxmax(), "hour_local"] \
        if peak_dc_y > 0 else 0

    print("SIMULATED vs OBSERVED (Feb 21, 2026):")
    print()
    print_hourly_table(sim_yesterday, observed=YESTERDAY_OBSERVED)
    print()
    print(f"  Daily DC energy:    {daily_dc_y:.2f} kWh")
    print(f"  Daily AC energy:    {daily_ac_y:.2f} kWh")
    print(f"  Simulated peak:     {peak_dc_y:.2f} kW DC at {int(peak_hour_y):02d}:00 CET")
    print()

    # Accuracy check
    obs_peak = YESTERDAY_OBSERVED["peak_kw"]
    delta = peak_dc_y - obs_peak
    pct = delta / obs_peak * 100
    status = "✅" if abs(pct) <= 30 else "⚠"
    print(f"  Model accuracy:     {status} Simulated {peak_dc_y:.2f} kW vs observed ~{obs_peak:.1f} kW peak")
    print(f"                      Δ = {delta:+.2f} kW ({pct:+.1f}%)")

    # ─ Today's prediction ────────────────────────────────────────────────────
    sep("Feb 22, 2026 – TODAY'S PREDICTION", "═")

    sim_today = simulate_day(location, system, wx_today, TODAY)

    daily_dc_t = sim_today["dc_kw"].sum()
    daily_ac_t = sim_today["ac_kw"].sum()
    peak_dc_t = sim_today["dc_kw"].max()
    peak_ac_t = sim_today["ac_kw"].max()
    peak_hour_t_row = sim_today.loc[sim_today["dc_kw"].idxmax()]
    peak_hour_t = int(peak_hour_t_row["hour_local"]) if peak_dc_t > 0 else 0

    production_hours = sim_today[sim_today["dc_kw"] > 0.05]

    print(f"  Date:              {TODAY.strftime('%A, %d %B %Y')}")
    print(f"  Production window: {int(production_hours['hour_local'].min()):02d}:00 – {int(production_hours['hour_local'].max()):02d}:00 CET "
          f"({len(production_hours)} hours)")
    print()
    print_hourly_table(sim_today)
    print()

    sep("SUMMARY", "─")
    print(f"  Daily DC energy:          {daily_dc_t:.2f} kWh")
    print(f"  Daily AC energy:          {daily_ac_t:.2f} kWh  (after {INVERTER_EFF*100:.0f}% inverter)")
    print(f"  Peak DC power:            {peak_dc_t:.2f} kW  at {peak_hour_t:02d}:00 CET")
    print(f"  Peak AC power:            {peak_ac_t:.2f} kW")
    print(f"  Capacity factor (24h):    {daily_dc_t / (TOTAL_WP/1000 * 24) * 100:.2f}%")
    print(f"  Specific yield:           {daily_dc_t / (TOTAL_WP/1000):.3f} kWh/kWp")
    print()

    # Day-over-day comparison
    sep("Day-over-Day Comparison", "─")
    change_peak = peak_dc_t - peak_dc_y
    change_energy = daily_dc_t - daily_dc_y
    print(f"  {'metric':<28} {'Feb 21 (actual)':<20} {'Feb 22 (predicted)':<20} {'Change':<12}")
    print(f"  {'─'*28} {'─'*20} {'─'*20} {'─'*12}")
    print(f"  {'Peak power (DC)':<28} {peak_dc_y:<20.2f} {peak_dc_t:<20.2f} {change_peak:+.2f} kW")
    print(f"  {'Daily energy (DC)':<28} {daily_dc_y:<20.2f} {daily_dc_t:<20.2f} {change_energy:+.2f} kWh")

    # Weather comparison
    prague_tz = pytz.timezone(TIMEZONE)
    noon_y = wx_yesterday.index.tz_convert(prague_tz)
    noon_t = wx_today.index.tz_convert(prague_tz)
    cloud_y_noon = wx_yesterday[noon_y.hour.isin([10,11,12,13,14])]["cloud_cover"].mean()
    cloud_t_noon = wx_today[noon_t.hour.isin([10,11,12,13,14])]["cloud_cover"].mean()
    print(f"  {'Cloud cover 10–14:00 CET':<28} {cloud_y_noon:<20.0f} {cloud_t_noon:<20.0f} {cloud_t_noon-cloud_y_noon:+.0f} %")

    ghi_y_noon = wx_yesterday[noon_y.hour.isin([10,11,12,13,14])]["ghi"].mean()
    ghi_t_noon = wx_today[noon_t.hour.isin([10,11,12,13,14])]["ghi"].mean()
    print(f"  {'GHI avg 10–14:00 CET':<28} {ghi_y_noon:<20.0f} {ghi_t_noon:<20.0f} {ghi_t_noon-ghi_y_noon:+.0f} W/m²")

    temp_y = wx_yesterday[noon_y.hour.isin([10,11,12,13,14])]["temp_air"].mean()
    temp_t = wx_today[noon_t.hour.isin([10,11,12,13,14])]["temp_air"].mean()
    print(f"  {'Temp avg 10–14:00 CET':<28} {temp_y:<20.1f} {temp_t:<20.1f} {temp_t-temp_y:+.1f} °C")
    print()

    # Qualitative summary
    sep("Qualitative Assessment", "─")
    if peak_dc_t > 6:
        level = "GOOD – partly sunny conditions"
        emoji = "🌤"
    elif peak_dc_t > 3:
        level = "MODERATE – significant cloud cover"
        emoji = "⛅"
    elif peak_dc_t > 1:
        level = "POOR – heavy overcast"
        emoji = "☁"
    else:
        level = "VERY POOR – almost no production"
        emoji = "🌫"

    print(f"  {emoji}  Today's outlook: {level}")
    print(f"  Estimated AC export: ~{daily_ac_t:.1f} kWh")
    print(f"  Economic value:      ~{daily_ac_t * 0.15:.2f} EUR  @ 0.15 EUR/kWh")
    print(f"  CO₂ avoided:         ~{daily_ac_t * 0.5:.2f} kg   (vs. grid mix)")
    print()

    # Model validation note
    print("  NOTE ON MODEL ACCURACY:")
    print(f"    Yesterday model predicted {peak_dc_y:.1f} kW peak,")
    print(f"    you observed ~{obs_peak:.1f} kW  →  model {'overestimates' if delta > 0 else 'underestimates'} by {abs(pct):.0f}%.")
    if abs(pct) <= 15:
        print("    ✅ Excellent agreement – today's prediction is reliable.")
    elif abs(pct) <= 30:
        print("    ✅ Good agreement – today's prediction should be close.")
    else:
        print("    ⚠  Larger deviation – today's prediction carries ~30% uncertainty.")
        print("       Likely cause: cloud distribution within VC hourly buckets.")
    print()
    sep()


if __name__ == "__main__":
    main()
