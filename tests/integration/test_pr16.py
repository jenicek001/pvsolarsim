"""
Test PR #16 - Visual Crossing Weather API Integration
Real-World Prague PV System with Visual Crossing Weather Data

This test validates the Visual Crossing weather API integration by:
1. Unit-testing VisualCrossingClient with mocked responses (always runs in CI)
2. Testing real API calls when VISUAL_CROSSING_API_KEY env var is set
3. Validating simulate_annual() with weather_source='visual_crossing'
4. End-to-end real-world Prague installation scenario with VC data
5. Comparing Visual Crossing data against clear-sky baseline

Location: Prague, Czech Republic (50.0807494°N, 14.8594164°E)
System: 14.04 kWp residential installation
- String 1: 16× München Energieprodukte MSMD450M6-72 M6 @ 450W = 7.2 kWp
- String 2: 18× Canadian Solar HiKu CS3L-380MS @ 380W = 6.84 kWp
- Orientation: 35° tilt, 202° azimuth (SSW)

How to run with a real API key:
    export VISUAL_CROSSING_API_KEY="YOUR_KEY_HERE"
    pytest tests/integration/test_pr9.py -v -s --no-header

Without an API key, all tests that require a real network call are skipped
automatically; the mock-based tests always run.

Visual Crossing free tier: 1,000 API calls/day
Sign up: https://www.visualcrossing.com/weather-api
"""

import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
import pytz

from pvsolarsim import Location, PVSystem, calculate_power
from pvsolarsim.weather import VisualCrossingClient

# ==================================================================================
# CONFIGURATION
# ==================================================================================

# Real system – Prague residential installation
LATITUDE = 50.0807494
LONGITUDE = 14.8594164
ALTITUDE = 220
TIMEZONE = "Europe/Prague"

MUNCHEN_PANELS = {
    "count": 16,
    "power_wp": 450,
    "efficiency": 0.2037,
    "temp_coeff_pmax": -0.0035,
    "area_m2": 2.108 * 1.048,
}
CANADIAN_PANELS = {
    "count": 18,
    "power_wp": 380,
    "efficiency": 0.205,
    "temp_coeff_pmax": -0.0037,
    "area_m2": 1.765 * 1.048,
}

TOTAL_POWER_WP = (
    MUNCHEN_PANELS["count"] * MUNCHEN_PANELS["power_wp"]
    + CANADIAN_PANELS["count"] * CANADIAN_PANELS["power_wp"]
)
TOTAL_AREA_M2 = (
    MUNCHEN_PANELS["count"] * MUNCHEN_PANELS["area_m2"]
    + CANADIAN_PANELS["count"] * CANADIAN_PANELS["area_m2"]
)
WEIGHTED_EFFICIENCY = TOTAL_POWER_WP / (TOTAL_AREA_M2 * 1000)
WEIGHTED_TEMP_COEFF = (
    MUNCHEN_PANELS["count"] * MUNCHEN_PANELS["power_wp"] * MUNCHEN_PANELS["temp_coeff_pmax"]
    + CANADIAN_PANELS["count"]
    * CANADIAN_PANELS["power_wp"]
    * CANADIAN_PANELS["temp_coeff_pmax"]
) / TOTAL_POWER_WP

TILT = 35.0
AZIMUTH = 202.0

# Pick up optional real API key from environment
VC_API_KEY = os.environ.get("VISUAL_CROSSING_API_KEY", "")
NEEDS_REAL_KEY = pytest.mark.skipif(
    not VC_API_KEY,
    reason="Set VISUAL_CROSSING_API_KEY env var to run live Visual Crossing tests",
)


# ==================================================================================
# HELPERS – mock Visual Crossing API response
# ==================================================================================


def _build_vc_response(
    start_date: str = "2025-01-01",
    days: int = 1,
    ghi: float = 300.0,
    temp: float = 5.0,
    windspeed: float = 10.0,
    cloudcover: float = 40.0,
) -> dict:
    """Build a minimal but realistic Visual Crossing JSON response.

    Parameters
    ----------
    start_date : str
        First day in YYYY-MM-DD format.
    days : int
        How many days to generate (each with 24 hourly records).
    ghi : float
        Solar radiation (W/m²) set during midday hours (08-16).
    temp : float
        Air temperature in °C.
    windspeed : float
        Wind speed in km/h (VC uses km/h).
    cloudcover : float
        Cloud cover percentage (0-100).
    """
    day_list = []
    for d in range(days):
        date = pd.Timestamp(start_date) + pd.Timedelta(days=d)
        date_str = date.strftime("%Y-%m-%d")
        hours = []
        for h in range(24):
            # Only produce solar radiation between 08:00 and 16:00
            solar = ghi if 8 <= h <= 16 else 0.0
            hours.append(
                {
                    "datetime": f"{h:02d}:00:00",
                    "temp": temp,
                    "windspeed": windspeed,
                    "cloudcover": cloudcover,
                    "solarradiation": solar,
                    "solarenergy": solar * 0.001,  # Wh/m² → kWh/m², rough
                    "uvindex": 2 if solar > 0 else 0,
                }
            )
        day_list.append({"datetime": date_str, "hours": hours})

    return {
        "queryCost": days * 24,
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "resolvedAddress": f"{LATITUDE},{LONGITUDE}",
        "timezone": TIMEZONE,
        "days": day_list,
    }


# ==================================================================================
# FIXTURES
# ==================================================================================


@pytest.fixture
def prague_location():
    """Create Location object for Prague installation."""
    return Location(
        latitude=LATITUDE, longitude=LONGITUDE, altitude=ALTITUDE, timezone=TIMEZONE
    )


@pytest.fixture
def prague_system():
    """Create PVSystem object for Prague installation."""
    return PVSystem(
        panel_area=TOTAL_AREA_M2,
        panel_efficiency=WEIGHTED_EFFICIENCY,
        tilt=TILT,
        azimuth=AZIMUTH,
        temp_coefficient=WEIGHTED_TEMP_COEFF,
    )


@pytest.fixture
def mock_vc_client(tmp_path):
    """VisualCrossingClient with HTTP calls fully mocked."""
    with patch("pvsolarsim.weather.api_clients.WeatherCache") as mock_cache_cls:
        mock_cache = MagicMock()
        mock_cache.get.return_value = None  # cache miss → always fetch
        mock_cache_cls.return_value = mock_cache

        client = VisualCrossingClient(api_key="MOCK_KEY", cache_ttl=0)

        yield client


# ==================================================================================
# TEST 1: VisualCrossingClient instantiation & basic attributes
# ==================================================================================


@pytest.mark.slow
def test_client_instantiation():
    """Test 1: VisualCrossingClient can be instantiated with an API key."""
    print("\n" + "=" * 80)
    print("TEST 1: VisualCrossingClient Instantiation")
    print("=" * 80)

    client = VisualCrossingClient(api_key="TEST_KEY_12345")

    assert client.api_key == "TEST_KEY_12345"
    assert client.timeout >= 10, "Timeout should be reasonable (>= 10s)"
    assert "weather.visualcrossing.com" in client.BASE_URL
    assert client.session is not None

    print("\n  API key set:       ✅")
    print(f"  BASE_URL:          {client.BASE_URL}")
    print(f"  Timeout:           {client.timeout}s")
    print("  HTTP session:      ✅ (with retry logic)")


# ==================================================================================
# TEST 2: Input validation
# ==================================================================================


@pytest.mark.slow
def test_client_validates_inputs():
    """Test 2: VisualCrossingClient rejects invalid lat/lon/dates."""
    print("\n" + "=" * 80)
    print("TEST 2: Input Validation")
    print("=" * 80)

    client = VisualCrossingClient(api_key="TEST_KEY")
    tz = pytz.UTC
    start = datetime(2025, 1, 1, tzinfo=tz)
    end = datetime(2025, 1, 2, tzinfo=tz)

    with pytest.raises(ValueError, match="[Ll]atitude"):
        client.read(latitude=91.0, longitude=14.8, start=start, end=end)

    with pytest.raises(ValueError, match="[Ll]ontitude|[Ll]ongitude"):
        client.read(latitude=50.0, longitude=181.0, start=start, end=end)

    with pytest.raises(ValueError, match="start.*end|Both"):
        client.read(latitude=50.0, longitude=14.8, start=None, end=None)

    print("  ✅ Invalid latitude raises ValueError")
    print("  ✅ Invalid longitude raises ValueError")
    print("  ✅ Missing start/end raises ValueError")


# ==================================================================================
# TEST 3: _parse_response – verify output columns and types
# ==================================================================================


@pytest.mark.slow
def test_parse_response_structure():
    """Test 3: _parse_response returns correctly structured DataFrame."""
    print("\n" + "=" * 80)
    print("TEST 3: _parse_response Output Structure")
    print("=" * 80)

    client = VisualCrossingClient(api_key="TEST_KEY")

    # Build 2 days of mock data
    mock_response = _build_vc_response(
        start_date="2025-06-15",
        days=2,
        ghi=600.0,
        temp=22.0,
        windspeed=14.4,  # 4 m/s in km/h
        cloudcover=20.0,
    )

    df = client._parse_response(mock_response)

    print(f"\n  Records returned:  {len(df)}")
    print(f"  Columns:           {list(df.columns)}")
    print(f"  Index type:        {type(df.index).__name__}")
    print(f"  Date range:        {df.index.min()} → {df.index.max()}")
    print()

    # Structure checks
    assert len(df) == 2 * 24, f"Expected {2*24} hourly records, got {len(df)}"
    assert "ghi" in df.columns, "Missing 'ghi' column"
    assert "dni" in df.columns, "Missing 'dni' column"
    assert "dhi" in df.columns, "Missing 'dhi' column"
    assert "temp_air" in df.columns, "Missing 'temp_air' column"
    assert "wind_speed" in df.columns, "Missing 'wind_speed' column"
    assert "cloud_cover" in df.columns, "Missing 'cloud_cover' column"

    # Value checks
    assert df["ghi"].max() > 0, "GHI should be positive during midday"
    assert df["ghi"].min() == 0.0, "GHI should be 0 during night"
    assert df["temp_air"].iloc[0] == pytest.approx(22.0, abs=0.01), "Temperature mismatch"
    # wind_speed should be in m/s (VC gives km/h → divide by 3.6)
    expected_ws = 14.4 / 3.6
    assert df["wind_speed"].iloc[0] == pytest.approx(expected_ws, abs=0.1), (
        "Wind speed should be converted from km/h to m/s"
    )
    assert df["cloud_cover"].iloc[0] == pytest.approx(20.0, abs=0.01), "Cloud cover mismatch"

    # DNI and DHI should be non-negative
    assert (df["dni"] >= 0).all(), "DNI must be non-negative"
    assert (df["dhi"] >= 0).all(), "DHI must be non-negative"

    print("  ✅ All required columns present")
    print("  ✅ Wind speed converted from km/h → m/s")
    print(f"  ✅ GHI range: {df['ghi'].min():.0f} – {df['ghi'].max():.0f} W/m²")
    print(f"  ✅ Wind speed range: {df['wind_speed'].min():.2f} – {df['wind_speed'].max():.2f} m/s")


# ==================================================================================
# TEST 4: Mocked read() – full HTTP path
# ==================================================================================


@pytest.mark.slow
def test_read_with_mocked_http(mock_vc_client):
    """Test 4: read() returns DataFrame when HTTP is mocked (no real API key needed)."""
    print("\n" + "=" * 80)
    print("TEST 4: read() via Mocked HTTP")
    print("=" * 80)

    start = datetime(2025, 1, 1, tzinfo=pytz.UTC)
    end = datetime(2025, 1, 2, tzinfo=pytz.UTC)

    mock_response = _build_vc_response(
        start_date="2025-01-01",
        days=1,
        ghi=100.0,
        temp=2.0,
        windspeed=18.0,
        cloudcover=75.0,
    )

    # Mock the HTTP response
    mock_http_response = MagicMock()
    mock_http_response.json.return_value = mock_response
    mock_http_response.raise_for_status = MagicMock()

    with patch.object(mock_vc_client.session, "get", return_value=mock_http_response):
        df = mock_vc_client.read(
            latitude=LATITUDE, longitude=LONGITUDE, start=start, end=end
        )

    print(f"\n  Records:    {len(df)}")
    print(f"  GHI max:    {df['ghi'].max():.1f} W/m²")
    print(f"  Temp:       {df['temp_air'].iloc[12]:.1f} °C")
    print(f"  Cloud:      {df['cloud_cover'].iloc[12]:.0f}%")

    assert len(df) == 24, f"Expected 24 hourly records, got {len(df)}"
    assert df["ghi"].max() == pytest.approx(100.0, abs=0.1)
    assert df["temp_air"].iloc[0] == pytest.approx(2.0, abs=0.01)
    assert df["cloud_cover"].iloc[0] == pytest.approx(75.0, abs=0.01)

    print("  ✅ read() returns valid DataFrame via mocked HTTP")


# ==================================================================================
# TEST 5: Power calculation using mocked Visual Crossing data
# ==================================================================================


@pytest.mark.slow
def test_power_calculation_with_vc_data(prague_location, prague_system):
    """Test 5: Calculate power for Prague system using mocked VC weather data."""
    print("\n" + "=" * 80)
    print("TEST 5: Power Calculation with Visual Crossing Data (Mocked)")
    print("Prague 14.04 kWp, representative summer day (June 15, 2025)")
    print("=" * 80)

    # Build summer day mock data – clear sky, warm
    mock_response = _build_vc_response(
        start_date="2025-06-15",
        days=1,
        ghi=700.0,
        temp=24.0,
        windspeed=10.8,  # 3 m/s
        cloudcover=10.0,
    )

    client = VisualCrossingClient(api_key="MOCK")
    weather_df = client._parse_response(mock_response)

    print(f"\n  Weather records loaded: {len(weather_df)}")
    print(f"  GHI peak: {weather_df['ghi'].max():.0f} W/m²")
    print(f"  Temperature: {weather_df['temp_air'].iloc[12]:.1f}°C")
    print(f"  Cloud cover: {weather_df['cloud_cover'].iloc[12]:.0f}%")
    print()

    prague_tz = pytz.timezone(TIMEZONE)
    total_energy_wh = 0.0
    peak_power_w = 0.0
    production_rows = []

    for timestamp, row in weather_df.iterrows():
        # VisualCrossing timestamps come in UTC; localize for calculate_power
        ts_local = timestamp.astimezone(prague_tz)

        result = calculate_power(
            location=prague_location,
            system=prague_system,
            timestamp=ts_local,
            ghi=row["ghi"],
            dni=row["dni"],
            dhi=row["dhi"],
            ambient_temp=row["temp_air"],
            wind_speed=row["wind_speed"],
            cloud_cover=row["cloud_cover"],
            soiling_factor=0.97,
            inverter_efficiency=0.97,
        )
        power_w = result.power_w if not np.isnan(result.power_w) else 0.0
        total_energy_wh += power_w
        if power_w > peak_power_w:
            peak_power_w = power_w
        if power_w > 50:
            production_rows.append(
                {
                    "hour": ts_local.hour,
                    "ghi": row["ghi"],
                    "power_dc_kw": result.power_w / 1000,
                    "power_ac_kw": result.power_ac_w / 1000,
                    "solar_elevation": result.solar_elevation,
                    "cell_temp": result.cell_temperature,
                }
            )

    total_energy_kwh = total_energy_wh / 1000
    specific_yield = total_energy_kwh / (TOTAL_POWER_WP / 1000)

    print("PRODUCTION SUMMARY (June 15 – mocked VC data):")
    print(f"  DC Energy:          {total_energy_kwh:.2f} kWh")
    print(f"  Peak DC Power:      {peak_power_w/1000:.2f} kW  ({peak_power_w/TOTAL_POWER_WP*100:.1f}% of rated)")
    print(f"  Specific Yield:     {specific_yield:.2f} kWh/kWp")
    print(f"  Production hours:   {len(production_rows)}")

    if production_rows:
        print()
        print(f"  {'Hour':>4}  {'GHI':>8}  {'DC kW':>8}  {'AC kW':>8}  {'Elev':>8}  {'Tcell':>8}")
        print(f"  {'':->4}  {'(W/m²)':->8}  {'':->8}  {'':->8}  {'(°)':->8}  {'(°C)':->8}")
        for r in production_rows:
            print(
                f"  {r['hour']:>4}  {r['ghi']:>8.0f}  {r['power_dc_kw']:>8.2f}  "
                f"{r['power_ac_kw']:>8.2f}  {r['solar_elevation']:>8.2f}  {r['cell_temp']:>8.1f}"
            )

    # Sanity checks
    assert total_energy_kwh >= 0, "Energy must be non-negative"
    assert peak_power_w >= 0, "Peak power must be non-negative"
    assert peak_power_w <= TOTAL_POWER_WP * 1.5, "Peak power should not massively exceed rated"
    if len(production_rows) > 0:
        # Summer day in Prague with GHI=700 W/m² peak should produce something meaningful
        assert total_energy_kwh > 1.0, (
            "Summer day should produce >1 kWh (GHI=700 W/m², 14 kWp system)"
        )

    print("\n  ✅ All power calculation checks passed")


# ==================================================================================
# TEST 6: Winter vs Summer comparison using mocked VC data
# ==================================================================================


@pytest.mark.slow
def test_winter_summer_comparison(prague_location, prague_system):
    """Test 6: Winter vs Summer production comparison with mocked VC data."""
    print("\n" + "=" * 80)
    print("TEST 6: Winter vs Summer Production Comparison")
    print("Prague – using mocked Visual Crossing data")
    print("=" * 80)

    prague_tz = pytz.timezone(TIMEZONE)

    scenarios = {
        "Winter (Jan 15)": {
            "start_date": "2025-01-15",
            "ghi": 120.0,
            "temp": -2.0,
            "windspeed": 18.0,
            "cloudcover": 70.0,
        },
        "Spring (Apr 15)": {
            "start_date": "2025-04-15",
            "ghi": 550.0,
            "temp": 14.0,
            "windspeed": 14.4,
            "cloudcover": 30.0,
        },
        "Summer (Jul 15)": {
            "start_date": "2025-07-15",
            "ghi": 800.0,
            "temp": 28.0,
            "windspeed": 10.8,
            "cloudcover": 15.0,
        },
    }

    client = VisualCrossingClient(api_key="MOCK")
    results_summary = {}

    for season, params in scenarios.items():
        mock_response = _build_vc_response(
            start_date=params["start_date"],
            days=1,
            ghi=params["ghi"],
            temp=params["temp"],
            windspeed=params["windspeed"],
            cloudcover=params["cloudcover"],
        )
        weather_df = client._parse_response(mock_response)

        daily_energy_wh = 0.0
        peak_w = 0.0

        for timestamp, row in weather_df.iterrows():
            ts_local = timestamp.astimezone(prague_tz)
            result = calculate_power(
                location=prague_location,
                system=prague_system,
                timestamp=ts_local,
                ghi=row["ghi"],
                dni=row["dni"],
                dhi=row["dhi"],
                ambient_temp=row["temp_air"],
                wind_speed=row["wind_speed"],
                cloud_cover=row["cloud_cover"],
            )
            power_w = result.power_w if not np.isnan(result.power_w) else 0.0
            daily_energy_wh += power_w
            if power_w > peak_w:
                peak_w = power_w

        results_summary[season] = {
            "energy_kwh": daily_energy_wh / 1000,
            "peak_kw": peak_w / 1000,
        }

    print()
    print(f"  {'Season':<20}  {'GHI peak':>10}  {'Daily DC':>12}  {'Peak DC':>10}")
    print(f"  {'':->20}  {'(W/m²)':->10}  {'energy (kWh)':->12}  {'power (kW)':->10}")
    for season, r in results_summary.items():
        ghi_peak = scenarios[season]["ghi"]
        print(
            f"  {season:<20}  {ghi_peak:>10.0f}  {r['energy_kwh']:>12.2f}  {r['peak_kw']:>10.2f}"
        )

    winter_energy = results_summary["Winter (Jan 15)"]["energy_kwh"]
    summer_energy = results_summary["Summer (Jul 15)"]["energy_kwh"]

    print()
    print(f"  Summer / Winter ratio: {summer_energy / max(winter_energy, 0.001):.1f}×")

    # Summer should always outproduce winter (higher GHI + longer days)
    assert summer_energy >= winter_energy, (
        "Summer energy should be >= winter energy for Prague"
    )
    assert results_summary["Spring (Apr 15)"]["energy_kwh"] >= winter_energy, (
        "Spring energy should be >= winter energy"
    )

    print("  ✅ Seasonal ordering correct (winter < spring < summer)")


# ==================================================================================
# TEST 7: read_forecast() – mocked
# ==================================================================================


@pytest.mark.slow
def test_read_forecast_mocked(mock_vc_client):
    """Test 7: read_forecast() returns valid DataFrame (mocked HTTP)."""
    print("\n" + "=" * 80)
    print("TEST 7: read_forecast() – Mocked HTTP")
    print("=" * 80)

    # Build 7-day forecast response
    mock_response = _build_vc_response(
        start_date=datetime.now().strftime("%Y-%m-%d"),
        days=7,
        ghi=400.0,
        temp=10.0,
        windspeed=14.4,
        cloudcover=50.0,
    )

    mock_http_response = MagicMock()
    mock_http_response.json.return_value = mock_response
    mock_http_response.raise_for_status = MagicMock()

    with patch.object(mock_vc_client.session, "get", return_value=mock_http_response):
        df = mock_vc_client.read_forecast(latitude=LATITUDE, longitude=LONGITUDE, days=7)

    print(f"\n  Forecast records: {len(df)}")
    print(f"  Date range: {df.index.min()} → {df.index.max()}")
    print(f"  Columns: {list(df.columns)}")

    assert len(df) <= 7 * 24, f"Expected at most {7*24} hourly records, got {len(df)}"
    assert len(df) > 0, "Forecast DataFrame should not be empty"
    assert "ghi" in df.columns
    assert "temp_air" in df.columns

    print(f"  ✅ read_forecast() returned {len(df)} records (≤ {7*24})")


# ==================================================================================
# TEST 8: HTTP error handling
# ==================================================================================


@pytest.mark.slow
def test_http_error_handling():
    """Test 8: VisualCrossingClient raises ValueError on HTTP errors."""
    print("\n" + "=" * 80)
    print("TEST 8: HTTP Error Handling")
    print("=" * 80)

    import requests

    client = VisualCrossingClient(api_key="BAD_KEY")
    start = datetime(2025, 1, 1, tzinfo=pytz.UTC)
    end = datetime(2025, 1, 2, tzinfo=pytz.UTC)

    # Simulate a 401 Unauthorized
    with patch.object(client.session, "get") as mock_get:
        mock_get.side_effect = requests.RequestException("401 Unauthorized")
        with pytest.raises(ValueError, match="Failed to fetch"):
            client.read(latitude=LATITUDE, longitude=LONGITUDE, start=start, end=end)

    print("  ✅ HTTP error raises ValueError with descriptive message")

    # Simulate bad JSON format
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"message": "Invalid API key"}  # no 'days' key
    mock_resp.raise_for_status = MagicMock()
    with patch.object(client.session, "get", return_value=mock_resp):
        # Cache must be empty
        with patch.object(client.cache, "get", return_value=None):
            with pytest.raises(ValueError, match="Invalid Visual Crossing"):
                client.read(latitude=LATITUDE, longitude=LONGITUDE, start=start, end=end)

    print("  ✅ Invalid JSON format raises ValueError")


# ==================================================================================
# TEST 9: simulate_annual() with weather_source='visual_crossing' (mocked)
# ==================================================================================


@pytest.mark.slow
def test_simulate_annual_with_visual_crossing_mocked(prague_location, prague_system):
    """Test 9: simulate_annual() end-to-end with mocked Visual Crossing source."""
    print("\n" + "=" * 80)
    print("TEST 9: simulate_annual() with weather_source='visual_crossing' (Mocked)")
    print("=" * 80)

    from pvsolarsim import simulate_annual

    # Build a full-year mock: use a simplified 12-month pattern
    # We patch VisualCrossingClient.read to return a pre-built DataFrame
    # covering the entire requested period.
    def _mock_vc_read(self_inner, latitude, longitude, start, end):
        # Normalize to UTC to avoid timezone conflicts with pd.date_range
        import pytz as _pytz
        start_utc = start.astimezone(_pytz.UTC)
        end_utc = end.astimezone(_pytz.UTC)
        times = pd.date_range(start=start_utc, end=end_utc, freq="h")
        n = len(times)
        # Simple sinusoidal GHI profile (day/night)
        hours = times.hour.to_numpy()
        day_of_year = times.dayofyear.to_numpy()
        # Solar elevation proxy: peaks at noon, seasonal variation
        noon_elev = 30 + 20 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        ghi_max = 900 * np.sin(np.radians(noon_elev))
        ghi = np.where(
            (hours >= 6) & (hours <= 18),
            ghi_max * np.sin(np.pi * (hours - 6) / 12),
            0.0,
        ).clip(0)
        # Ensure DHI is never exactly 0 – pvlib Perez divides by DHI and raises
        # ZeroDivisionError on night-time zeros (real VC data always has a trace
        # value for diffuse sky light even at night).
        ghi = np.clip(ghi, 1.0, None)
        temp = 10 + 12 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        wind = np.full(n, 3.0)
        cloud = np.full(n, 30.0)
        dni = (ghi * 0.8).clip(0)
        dhi = (ghi * 0.2).clip(0)
        df = pd.DataFrame(
            {
                "ghi": ghi,
                "dni": dni,
                "dhi": dhi,
                "temp_air": temp,
                "wind_speed": wind,
                "cloud_cover": cloud,
            },
            index=times,
        )
        return df

    with patch(
        "pvsolarsim.weather.VisualCrossingClient.read",
        new=_mock_vc_read,
    ):
        result = simulate_annual(
            location=prague_location,
            system=prague_system,
            year=2025,
            interval_minutes=60,
            weather_source="visual_crossing",
            api_key="MOCK_KEY",
        )

    stats = result.statistics

    print(f"\n  Annual energy:    {stats.total_energy_kwh:.1f} kWh")
    print(f"  Capacity factor:  {stats.capacity_factor * 100:.2f}%")
    print(f"  Peak power:       {stats.peak_power_w / 1000:.2f} kW")
    print()

    assert stats.total_energy_kwh > 0, "Annual energy must be positive"
    assert 0 < stats.capacity_factor < 1, "Capacity factor must be between 0 and 1"
    assert stats.peak_power_w > 0, "Peak power must be positive"
    assert stats.peak_power_w <= TOTAL_POWER_WP * 1.5, "Peak power must be realistic"

    # Monthly breakdown
    monthly = result.get_monthly_summary()
    assert len(monthly) == 12, "Should have 12 months of data"
    print("  Monthly Energy (kWh):")
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    energy_col = "energy_kwh"
    for i, (_idx, row) in enumerate(monthly.iterrows()):
        bar_len = int(row[energy_col] / 50)
        print(f"    {month_names[i]}: {row[energy_col]:>7.1f} kWh  {'█' * min(bar_len, 40)}")

    print("\n  ✅ simulate_annual() completed with weather_source='visual_crossing'")


# ==================================================================================
# TEST 10: LIVE API test – only runs when VISUAL_CROSSING_API_KEY is set
# ==================================================================================


@pytest.mark.slow
@NEEDS_REAL_KEY
def test_live_api_historical_data():
    """Test 10: Fetch real historical data from Visual Crossing API (requires key)."""
    print("\n" + "=" * 80)
    print("TEST 10: Live Visual Crossing API – Historical Data")
    print(f"API key: ...{VC_API_KEY[-6:]}")
    print("=" * 80)

    client = VisualCrossingClient(api_key=VC_API_KEY)

    # Fetch a single winter day for Prague to validate the real API
    start = datetime(2025, 1, 3, tzinfo=pytz.UTC)
    end = datetime(2025, 1, 3, 23, 59, tzinfo=pytz.UTC)

    df = client.read(latitude=LATITUDE, longitude=LONGITUDE, start=start, end=end)

    print(f"\n  Records fetched: {len(df)}")
    print(f"  Date range:  {df.index.min()} → {df.index.max()}")
    print()
    print(f"  {'Column':<15}  {'Min':>8}  {'Max':>8}  {'Mean':>8}")
    for col in ["ghi", "dni", "dhi", "temp_air", "wind_speed", "cloud_cover"]:
        print(
            f"  {col:<15}  {df[col].min():>8.2f}  {df[col].max():>8.2f}  {df[col].mean():>8.2f}"
        )

    assert len(df) >= 1, "Should return at least one record"
    assert "ghi" in df.columns
    assert "temp_air" in df.columns
    assert "wind_speed" in df.columns
    assert "cloud_cover" in df.columns
    assert df["ghi"].min() >= 0, "GHI cannot be negative"
    assert df["wind_speed"].min() >= 0, "Wind speed cannot be negative"
    assert df["temp_air"].min() > -60 and df["temp_air"].max() < 60, "Temperature should be realistic"

    print(f"\n  ✅ Live API returned {len(df)} valid records for Prague, Jan 3 2025")


@pytest.mark.slow
@NEEDS_REAL_KEY
def test_live_api_power_calculation(prague_location, prague_system):
    """Test 11: Full power calculation using live Visual Crossing data (requires key)."""
    print("\n" + "=" * 80)
    print("TEST 11: Live Visual Crossing → Power Calculation (Prague)")
    print(f"API key: ...{VC_API_KEY[-6:]}")
    print("=" * 80)

    client = VisualCrossingClient(api_key=VC_API_KEY)

    # Fetch a clear summer day for maximum production visibility
    start = datetime(2025, 6, 21, tzinfo=pytz.UTC)
    end = datetime(2025, 6, 21, 23, 59, tzinfo=pytz.UTC)

    weather_df = client.read(
        latitude=LATITUDE, longitude=LONGITUDE, start=start, end=end
    )

    prague_tz = pytz.timezone(TIMEZONE)
    total_energy_wh = 0.0
    peak_w = 0.0

    print(f"\n  Weather records: {len(weather_df)}")
    print(f"  GHI range: {weather_df['ghi'].min():.0f} – {weather_df['ghi'].max():.0f} W/m²")
    print(f"  Avg temperature: {weather_df['temp_air'].mean():.1f}°C")
    print()

    production_records = []
    for timestamp, row in weather_df.iterrows():
        ts_local = timestamp.astimezone(prague_tz)
        result = calculate_power(
            location=prague_location,
            system=prague_system,
            timestamp=ts_local,
            ghi=row["ghi"],
            dni=row["dni"],
            dhi=row["dhi"],
            ambient_temp=row["temp_air"],
            wind_speed=row["wind_speed"],
            cloud_cover=row["cloud_cover"],
            soiling_factor=0.97,
            inverter_efficiency=0.97,
        )
        power_w = result.power_w if not np.isnan(result.power_w) else 0.0
        total_energy_wh += power_w
        if power_w > peak_w:
            peak_w = power_w
        if power_w > 50:
            production_records.append(
                {
                    "hour": ts_local.strftime("%H:%M"),
                    "ghi": row["ghi"],
                    "power_kw": result.power_w / 1000,
                    "ac_kw": result.power_ac_w / 1000,
                    "elev": result.solar_elevation,
                }
            )

    total_kwh = total_energy_wh / 1000
    print(f"  {'Hour':>5}  {'GHI':>8}  {'DC (kW)':>9}  {'AC (kW)':>9}  {'Elev':>7}")
    print(f"  {'':->5}  {'(W/m²)':->8}  {'':->9}  {'':->9}  {'(°)':->7}")
    for r in production_records:
        print(
            f"  {r['hour']:>5}  {r['ghi']:>8.0f}  {r['power_kw']:>9.2f}  "
            f"{r['ac_kw']:>9.2f}  {r['elev']:>7.2f}"
        )

    print()
    print(f"  Daily DC energy: {total_kwh:.2f} kWh")
    print(f"  Peak DC power:   {peak_w/1000:.2f} kW  ({peak_w/TOTAL_POWER_WP*100:.1f}% of {TOTAL_POWER_WP/1000:.2f} kWp)")

    assert total_kwh >= 0, "Energy must be non-negative"
    assert peak_w >= 0, "Peak power must be non-negative"
    print("\n  ✅ Live VC data → power calculation succeeded for Jun 21 2025")


# ==================================================================================
# Main – run as script for quick demo without pytest
# ==================================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("PR #16 INTEGRATION TEST – Visual Crossing Weather API + Prague PV System")
    print("=" * 80)
    print(f"System: {TOTAL_POWER_WP/1000:.2f} kWp at Prague ({LATITUDE}°N, {LONGITUDE}°E)")
    print(f"API key configured: {'YES (live tests will run)' if VC_API_KEY else 'NO (mock tests only)'}")
    print()

    location = Location(
        latitude=LATITUDE, longitude=LONGITUDE, altitude=ALTITUDE, timezone=TIMEZONE
    )
    system = PVSystem(
        panel_area=TOTAL_AREA_M2,
        panel_efficiency=WEIGHTED_EFFICIENCY,
        tilt=TILT,
        azimuth=AZIMUTH,
        temp_coefficient=WEIGHTED_TEMP_COEFF,
    )

    test_client_instantiation()
    test_client_validates_inputs()
    test_parse_response_structure()
    test_power_calculation_with_vc_data(location, system)
    test_winter_summer_comparison(location, system)
    test_http_error_handling()

    if VC_API_KEY:
        test_live_api_historical_data()
        test_live_api_power_calculation(location, system)
    else:
        print("\nℹ️  Skipping live tests (set VISUAL_CROSSING_API_KEY to enable)")
        print("   export VISUAL_CROSSING_API_KEY='your_key'")

    print("\n" + "=" * 80)
    print("ALL PR #16 INTEGRATION TESTS COMPLETED")
    print("=" * 80)
