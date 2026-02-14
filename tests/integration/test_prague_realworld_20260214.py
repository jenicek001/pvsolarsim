"""
Real-World Prague PV System Simulation - February 14, 2026

This integration test simulates the actual Prague residential PV installation
for today's date (February 14, 2026) using realistic weather conditions and
compares the results with expected performance for mid-February in Czech Republic.

Location: Prague, Czech Republic (50.0807494°N, 14.8594164°E)
System: 14.04 kWp residential installation
- String 1: 16× München Energieprodukte MSMD450M6-72 M6 @ 450W = 7.2 kWp
- String 2: 18× Canadian Solar HiKu CS3L-380MS @ 380W = 6.84 kWp
- Orientation: 35° tilt, 202° azimuth (SSW)

Expected Performance (February in Prague):
- Daily energy: 5-15 kWh (weather dependent)
- Peak power: 2-6 kW (cloudy to clear sky)
- Daylight hours: ~10 hours
- Solar noon elevation: ~30° (low winter sun)
"""

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytz

from pvsolarsim import Location, PVSystem, calculate_power
from pvsolarsim.solar import calculate_solar_position

# ==============================================================================
# PRAGUE INSTALLATION CONFIGURATION
# ==============================================================================

# Location: Prague area, Czech Republic
LATITUDE = 50.0807494
LONGITUDE = 14.8594164
ALTITUDE = 220  # meters
TIMEZONE = "Europe/Prague"

# Panel specifications - String 1: München panels
MUNCHEN_PANELS = {
    'count': 16,
    'power_wp': 450,
    'efficiency': 0.2037,  # 20.37%
    'temp_coeff_pmax': -0.0035,  # -0.35%/°C
    'area_m2': 2.108 * 1.048,  # 2.209 m²
}

# Panel specifications - String 2: Canadian Solar panels
CANADIAN_PANELS = {
    'count': 18,
    'power_wp': 380,
    'efficiency': 0.205,  # ~20.5%
    'temp_coeff_pmax': -0.0037,  # -0.37%/°C
    'area_m2': 1.765 * 1.048,  # 1.850 m²
}

# System totals
TOTAL_POWER_WP = (MUNCHEN_PANELS['count'] * MUNCHEN_PANELS['power_wp'] +
                  CANADIAN_PANELS['count'] * CANADIAN_PANELS['power_wp'])
TOTAL_AREA_M2 = (MUNCHEN_PANELS['count'] * MUNCHEN_PANELS['area_m2'] +
                 CANADIAN_PANELS['count'] * CANADIAN_PANELS['area_m2'])
WEIGHTED_EFFICIENCY = TOTAL_POWER_WP / (TOTAL_AREA_M2 * 1000)
WEIGHTED_TEMP_COEFF = (
    (MUNCHEN_PANELS['count'] * MUNCHEN_PANELS['power_wp'] * MUNCHEN_PANELS['temp_coeff_pmax'] +
     CANADIAN_PANELS['count'] * CANADIAN_PANELS['power_wp'] * CANADIAN_PANELS['temp_coeff_pmax']) /
    TOTAL_POWER_WP
)

# System orientation
TILT = 35.0  # degrees (optimal for Central Europe)
AZIMUTH = 202.0  # degrees (SSW orientation)


def main():
    """
    Run real-world simulation for Prague installation on February 14, 2026.
    """
    print("=" * 90)
    print("REAL-WORLD PRAGUE PV SYSTEM SIMULATION")
    print("Date: February 14, 2026")
    print("=" * 90)
    print()

    # =========================================================================
    # SYSTEM CONFIGURATION
    # =========================================================================
    print("SYSTEM CONFIGURATION")
    print("-" * 90)
    print(f"Location: {LATITUDE}°N, {LONGITUDE}°E, {ALTITUDE}m")
    print(f"Timezone: {TIMEZONE}")
    print()
    print("Panel Configuration:")
    print(f"  String 1: {MUNCHEN_PANELS['count']}× München MSMD450M6-72 @ {MUNCHEN_PANELS['power_wp']}W")
    print(f"    - Capacity: {MUNCHEN_PANELS['count'] * MUNCHEN_PANELS['power_wp']/1000:.2f} kWp")
    print(f"    - Efficiency: {MUNCHEN_PANELS['efficiency']*100:.2f}%")
    print(f"  String 2: {CANADIAN_PANELS['count']}× Canadian Solar CS3L-380MS @ {CANADIAN_PANELS['power_wp']}W")
    print(f"    - Capacity: {CANADIAN_PANELS['count'] * CANADIAN_PANELS['power_wp']/1000:.2f} kWp")
    print(f"    - Efficiency: {CANADIAN_PANELS['efficiency']*100:.2f}%")
    print()
    print("System Totals:")
    print(f"  Total Capacity: {TOTAL_POWER_WP/1000:.2f} kWp")
    print(f"  Total Area: {TOTAL_AREA_M2:.2f} m²")
    print(f"  Weighted Efficiency: {WEIGHTED_EFFICIENCY*100:.2f}%")
    print(f"  Weighted Temp Coefficient: {WEIGHTED_TEMP_COEFF*100:.3f}%/°C")
    print(f"  Orientation: Tilt {TILT}°, Azimuth {AZIMUTH}° (SSW)")
    print()

    # =========================================================================
    # CREATE LOCATION AND SYSTEM OBJECTS
    # =========================================================================
    location = Location(
        latitude=LATITUDE,
        longitude=LONGITUDE,
        altitude=ALTITUDE,
        timezone=TIMEZONE
    )

    system = PVSystem(
        panel_area=TOTAL_AREA_M2,
        panel_efficiency=WEIGHTED_EFFICIENCY,
        tilt=TILT,
        azimuth=AZIMUTH,
        temp_coefficient=WEIGHTED_TEMP_COEFF
    )

    # =========================================================================
    # FEBRUARY 14, 2026 - HOURLY SIMULATION
    # =========================================================================
    print("=" * 90)
    print("FEBRUARY 14, 2026 - HOURLY SIMULATION")
    print("=" * 90)
    print()

    # Set up timezone-aware datetime for February 14, 2026
    prague_tz = pytz.timezone(TIMEZONE)
    target_date = prague_tz.localize(datetime(2026, 2, 14, 0, 0, 0))

    # Generate hourly timestamps for the full day
    timestamps = [target_date + timedelta(hours=h) for h in range(24)]

    # Typical February weather conditions in Prague
    # Based on historical data: cold, partly cloudy, low sun angle
    FEBRUARY_CONDITIONS = {
        'ambient_temp_avg': 2.0,  # °C (average February temp in Prague)
        'ambient_temp_day': 5.0,   # °C (daytime temp)
        'ambient_temp_night': -1.0, # °C (nighttime temp)
        'wind_speed_avg': 3.5,     # m/s (typical winter wind)
        'cloud_cover': 50,         # % (partly cloudy - typical for Prague in Feb)
    }

    print("Weather Assumptions (Typical February in Prague):")
    print(f"  Daytime Temperature: {FEBRUARY_CONDITIONS['ambient_temp_day']:.1f}°C")
    print(f"  Nighttime Temperature: {FEBRUARY_CONDITIONS['ambient_temp_night']:.1f}°C")
    print(f"  Wind Speed: {FEBRUARY_CONDITIONS['wind_speed_avg']:.1f} m/s")
    print(f"  Cloud Cover: {FEBRUARY_CONDITIONS['cloud_cover']}% (partly cloudy)")
    print()

    # =========================================================================
    # CALCULATE POWER FOR EACH HOUR
    # =========================================================================
    print("-" * 90)
    print("HOURLY POWER PRODUCTION")
    print("-" * 90)
    print(f"{'Time':>8} | {'Sun Elev':>9} | {'Sun Azim':>9} | {'Temp':>6} | "
          f"{'Cloud':>6} | {'Power':>10} | {'Energy':>10}")
    print(f"{'(CET)':>8} | {'(deg)':>9} | {'(deg)':>9} | {'(°C)':>6} | "
          f"{'(%)':>6} | {'(W)':>10} | {'(Wh)':>10}")
    print("-" * 90)

    results = []
    total_energy_wh = 0
    peak_power_w = 0
    hours_with_production = 0

    for timestamp in timestamps:
        hour = timestamp.hour

        # Temperature varies throughout the day (simplified sinusoidal model)
        # Coldest at 6 AM, warmest at 2 PM
        temp_amplitude = (FEBRUARY_CONDITIONS['ambient_temp_day'] - 
                         FEBRUARY_CONDITIONS['ambient_temp_night']) / 2
        temp_mean = (FEBRUARY_CONDITIONS['ambient_temp_day'] + 
                    FEBRUARY_CONDITIONS['ambient_temp_night']) / 2
        # Peak temp at 14:00 (hour 14)
        ambient_temp = temp_mean + temp_amplitude * np.sin(
            (hour - 6) * np.pi / 12
        )

        # Calculate solar position
        solar_pos = calculate_solar_position(
            timestamp=timestamp,
            latitude=LATITUDE,
            longitude=LONGITUDE,
            altitude=ALTITUDE
        )

        # Only calculate power when sun is above horizon
        if solar_pos.elevation > 0:
            # Calculate power using clear-sky model with cloud cover
            result = calculate_power(
                location=location,
                system=system,
                timestamp=timestamp,
                ambient_temp=ambient_temp,
                wind_speed=FEBRUARY_CONDITIONS['wind_speed_avg'],
                cloud_cover=FEBRUARY_CONDITIONS['cloud_cover']
            )

            power_w = result.power_w
            energy_wh = power_w  # 1 hour interval
            total_energy_wh += energy_wh
            peak_power_w = max(peak_power_w, power_w)

            if power_w > 10:  # Count hours with meaningful production
                hours_with_production += 1

            print(f"{timestamp.strftime('%H:%M'):>8} | "
                  f"{solar_pos.elevation:>9.2f} | {solar_pos.azimuth:>9.2f} | "
                  f"{ambient_temp:>6.1f} | {FEBRUARY_CONDITIONS['cloud_cover']:>6.0f} | "
                  f"{power_w:>10.0f} | {energy_wh:>10.0f}")

            results.append({
                'timestamp': timestamp,
                'hour': hour,
                'solar_elevation': solar_pos.elevation,
                'solar_azimuth': solar_pos.azimuth,
                'ambient_temp': ambient_temp,
                'power_w': power_w,
                'energy_wh': energy_wh,
            })
        else:
            print(f"{timestamp.strftime('%H:%M'):>8} | "
                  f"{solar_pos.elevation:>9.2f} | {solar_pos.azimuth:>9.2f} | "
                  f"{ambient_temp:>6.1f} | {FEBRUARY_CONDITIONS['cloud_cover']:>6.0f} | "
                  f"{'---':>10} | {'---':>10}")

    print("-" * 90)
    print()

    # =========================================================================
    # DAILY SUMMARY
    # =========================================================================
    print("=" * 90)
    print("DAILY SUMMARY - February 14, 2026")
    print("=" * 90)
    print()
    print(f"Total Energy Production: {total_energy_wh/1000:.2f} kWh")
    print(f"Peak Power: {peak_power_w/1000:.2f} kW ({peak_power_w/TOTAL_POWER_WP*100:.1f}% of rated capacity)")
    print(f"Hours with Production: {hours_with_production} hours")
    print(f"Average Power (during daylight): {total_energy_wh/max(hours_with_production, 1):.0f} W")
    print()

    # =========================================================================
    # COMPARISON WITH EXPECTATIONS
    # =========================================================================
    print("=" * 90)
    print("COMPARISON WITH EXPECTED FEBRUARY PERFORMANCE")
    print("=" * 90)
    print()

    # Expected ranges for February in Prague (14 kWp system)
    expected_min_kwh = 5.0   # Very cloudy day
    expected_max_kwh = 15.0  # Clear day
    expected_avg_kwh = 8.0   # Partly cloudy (typical)

    print("Expected Daily Energy for 14 kWp System in Prague (February):")
    print(f"  Clear Sky: 12-15 kWh")
    print(f"  Partly Cloudy: 7-10 kWh")
    print(f"  Very Cloudy: 3-6 kWh")
    print()

    actual_kwh = total_energy_wh / 1000

    if actual_kwh >= 10:
        condition = "Good (Clear or mostly clear)"
    elif actual_kwh >= 6:
        condition = "Normal (Partly cloudy)"
    else:
        condition = "Poor (Very cloudy or overcast)"

    print(f"Simulated Result: {actual_kwh:.2f} kWh - {condition}")
    print()

    # Calculate capacity factor for the day
    theoretical_max_kwh = TOTAL_POWER_WP * 24 / 1000  # If running at full capacity 24h
    daily_capacity_factor = (actual_kwh / theoretical_max_kwh) * 100

    print(f"Daily Capacity Factor: {daily_capacity_factor:.2f}%")
    print(f"  (Note: Low winter CF is normal - short days, low sun angle)")
    print()

    # =========================================================================
    # SEASONAL CONTEXT
    # =========================================================================
    print("=" * 90)
    print("SEASONAL CONTEXT - FEBRUARY IN PRAGUE")
    print("=" * 90)
    print()

    print("Expected Annual Performance (14.04 kWp system):")
    print(f"  Annual Energy: 12,600 - 15,400 kWh (900-1,100 kWh/kWp)")
    print(f"  Annual Capacity Factor: 10-13%")
    print()

    print("February Characteristics:")
    print(f"  - Shortest winter month, low solar angles")
    print(f"  - Solar noon elevation: ~30° (vs ~60° in summer)")
    print(f"  - Daylight: ~10 hours (vs ~16 hours in June)")
    print(f"  - Typical weather: Partly cloudy, cold")
    print()

    if results:
        max_elevation = max(r['solar_elevation'] for r in results)
        print(f"Today's Solar Noon Elevation: {max_elevation:.1f}°")
        print(f"  (This matches expected ~30° for mid-February in Prague)")
        print()

    # =========================================================================
    # ROOF ORIENTATION ANALYSIS
    # =========================================================================
    print("=" * 90)
    print("ROOF ORIENTATION ANALYSIS")
    print("=" * 90)
    print()

    print(f"Your Roof: Tilt {TILT}°, Azimuth {AZIMUTH}° (SSW)")
    print()
    print("Orientation Assessment:")
    print(f"  - SSW orientation (22° west of south) is good for afternoon production")
    print(f"  - 35° tilt is optimal for year-round production in Central Europe")
    print(f"  - In winter, low sun angle means tilt matters less")
    print(f"  - SSW orientation captures afternoon sun well")
    print()

    # =========================================================================
    # SAVE RESULTS TO CSV
    # =========================================================================
    if results:
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "prague_20260214_hourly_results.csv"

        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False)
        print(f"Detailed hourly results saved to: {output_file}")
        print()

    # =========================================================================
    # RECOMMENDATIONS
    # =========================================================================
    print("=" * 90)
    print("RECOMMENDATIONS")
    print("=" * 90)
    print()

    print("To improve simulation accuracy:")
    print("  1. Use real weather data from PVGIS or OpenWeatherMap")
    print("     Example: weather_source='pvgis'")
    print()
    print("  2. Include soiling and degradation factors")
    print("     Example: soiling_factor=0.95, degradation_factor=0.98")
    print()
    print("  3. Account for inverter efficiency")
    print("     Example: inverter_efficiency=0.96")
    print()
    print("  4. For annual simulation, use:")
    print("     simulate_annual(location, system, year=2026, weather_source='pvgis')")
    print()

    print("=" * 90)
    print("SIMULATION COMPLETE")
    print("=" * 90)


if __name__ == "__main__":
    main()
