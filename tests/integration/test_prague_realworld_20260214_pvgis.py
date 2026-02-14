"""
Real-World Prague PV System Simulation - February 14, 2026
WITH PVGIS TYPICAL METEOROLOGICAL YEAR (TMY) DATA

This version attempts to use PVGIS TMY data for more realistic simulation.
If PVGIS is not available, it falls back to clear-sky with realistic cloud cover.

Location: Prague, Czech Republic (50.0807494°N, 14.8594164°E)
System: 14.04 kWp residential installation
"""

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytz

from pvsolarsim import Location, PVSystem, calculate_power, simulate_annual
from pvsolarsim.solar import calculate_solar_position

# ==============================================================================
# PRAGUE INSTALLATION CONFIGURATION
# ==============================================================================

# Location: Prague area, Czech Republic
LATITUDE = 50.0807494
LONGITUDE = 14.8594164
ALTITUDE = 220  # meters
TIMEZONE = "Europe/Prague"

# System totals (from test_pr8.py)
TOTAL_POWER_WP = 14040  # 7200 + 6840
TOTAL_AREA_M2 = 68.64
WEIGHTED_EFFICIENCY = 0.2045
WEIGHTED_TEMP_COEFF = -0.0036

# System orientation
TILT = 35.0  # degrees
AZIMUTH = 202.0  # degrees (SSW)


def simulate_with_pvgis():
    """Try to simulate using PVGIS TMY data."""
    print("=" * 90)
    print("ATTEMPTING PVGIS TMY DATA SIMULATION")
    print("=" * 90)
    print()

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

    try:
        print("Fetching PVGIS TMY data for Prague...")
        print("(This may take a moment...)")
        print()

        # Try to simulate with PVGIS
        results = simulate_annual(
            location=location,
            system=system,
            year=2026,
            interval_minutes=60,  # Hourly data
            weather_source='pvgis'
        )

        print("✓ PVGIS data fetched successfully!")
        print()

        # Extract February 14 data
        feb_14_data = results.time_series[
            (results.time_series.index.month == 2) &
            (results.time_series.index.day == 14)
        ]

        if len(feb_14_data) > 0:
            print("=" * 90)
            print("FEBRUARY 14, 2026 - HOURLY SIMULATION (PVGIS TMY DATA)")
            print("=" * 90)
            print()
            print(f"{'Time':>8} | {'Power':>10} | {'Energy':>10}")
            print(f"{'(CET)':>8} | {'(W)':>10} | {'(Wh)':>10}")
            print("-" * 40)

            daily_total_kwh = 0
            peak_power_w = 0

            for timestamp, power in feb_14_data.items():
                print(f"{timestamp.strftime('%H:%M'):>8} | {power:>10.0f} | {power:>10.0f}")
                daily_total_kwh += power / 1000  # Convert to kWh
                peak_power_w = max(peak_power_w, power)

            print("-" * 40)
            print()
            print("DAILY SUMMARY (PVGIS TMY):")
            print(f"  Total Energy: {daily_total_kwh:.2f} kWh")
            print(f"  Peak Power: {peak_power_w/1000:.2f} kW")
            print()

            return True, daily_total_kwh, peak_power_w

    except Exception as e:
        print(f"✗ PVGIS fetch failed: {e}")
        print()
        print("This is expected if:")
        print("  - No internet connection")
        print("  - PVGIS API is unavailable")
        print("  - Rate limiting")
        print()

    return False, 0, 0


def simulate_realistic_clearsky():
    """Simulate with clear-sky model but more realistic February conditions."""
    print("=" * 90)
    print("CLEAR-SKY SIMULATION WITH REALISTIC FEBRUARY CONDITIONS")
    print("=" * 90)
    print()

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

    # Set up timezone-aware datetime for February 14, 2026
    prague_tz = pytz.timezone(TIMEZONE)
    target_date = prague_tz.localize(datetime(2026, 2, 14, 0, 0, 0))

    # Generate hourly timestamps for the full day
    timestamps = [target_date + timedelta(hours=h) for h in range(24)]

    # More realistic February conditions (conservative estimates)
    # Prague in February: typically overcast to partly cloudy
    SCENARIOS = {
        'clear': {
            'name': 'Clear Sky (Optimistic)',
            'cloud_cover': 10,
            'ambient_temp_day': 7.0,
            'ambient_temp_night': 1.0,
            'wind_speed': 2.0,
        },
        'partly_cloudy': {
            'name': 'Partly Cloudy (Typical)',
            'cloud_cover': 60,
            'ambient_temp_day': 5.0,
            'ambient_temp_night': -1.0,
            'wind_speed': 3.5,
        },
        'overcast': {
            'name': 'Overcast (Pessimistic)',
            'cloud_cover': 85,
            'ambient_temp_day': 3.0,
            'ambient_temp_night': -2.0,
            'wind_speed': 4.5,
        }
    }

    results_by_scenario = {}

    for scenario_key, conditions in SCENARIOS.items():
        print(f"\nScenario: {conditions['name']}")
        print(f"  Cloud Cover: {conditions['cloud_cover']}%")
        print(f"  Temperature: {conditions['ambient_temp_night']:.1f}°C to {conditions['ambient_temp_day']:.1f}°C")
        print(f"  Wind Speed: {conditions['wind_speed']:.1f} m/s")
        print()

        total_energy_wh = 0
        peak_power_w = 0

        for timestamp in timestamps:
            hour = timestamp.hour

            # Temperature varies throughout the day
            temp_amplitude = (conditions['ambient_temp_day'] - 
                             conditions['ambient_temp_night']) / 2
            temp_mean = (conditions['ambient_temp_day'] + 
                        conditions['ambient_temp_night']) / 2
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
                result = calculate_power(
                    location=location,
                    system=system,
                    timestamp=timestamp,
                    ambient_temp=ambient_temp,
                    wind_speed=conditions['wind_speed'],
                    cloud_cover=conditions['cloud_cover']
                )

                total_energy_wh += result.power_w
                peak_power_w = max(peak_power_w, result.power_w)

        results_by_scenario[scenario_key] = {
            'energy_kwh': total_energy_wh / 1000,
            'peak_kw': peak_power_w / 1000,
        }

        print(f"  Daily Energy: {total_energy_wh/1000:.2f} kWh")
        print(f"  Peak Power: {peak_power_w/1000:.2f} kW")

    print()
    print("=" * 90)
    print("CLEAR-SKY SCENARIOS SUMMARY")
    print("=" * 90)
    print()
    print(f"{'Scenario':<25} | {'Daily Energy':<15} | {'Peak Power':<12}")
    print("-" * 60)
    for scenario_key, conditions in SCENARIOS.items():
        res = results_by_scenario[scenario_key]
        print(f"{conditions['name']:<25} | {res['energy_kwh']:>10.2f} kWh | {res['peak_kw']:>7.2f} kW")
    print()

    return results_by_scenario


def main():
    """Main simulation runner."""
    print("\n" * 2)
    print("=" * 90)
    print("REAL-WORLD PRAGUE PV SYSTEM SIMULATION - FEBRUARY 14, 2026")
    print("14.04 kWp Residential Installation")
    print("=" * 90)
    print()

    print("SYSTEM CONFIGURATION")
    print("-" * 90)
    print(f"Location: {LATITUDE}°N, {LONGITUDE}°E, {ALTITUDE}m")
    print(f"System Capacity: {TOTAL_POWER_WP/1000:.2f} kWp")
    print(f"Panel Area: {TOTAL_AREA_M2:.2f} m²")
    print(f"Orientation: {TILT}° tilt, {AZIMUTH}° azimuth (SSW)")
    print()

    # Try PVGIS first
    pvgis_success, pvgis_kwh, pvgis_peak = simulate_with_pvgis()

    # Always run clear-sky scenarios for comparison
    print()
    clearsky_results = simulate_realistic_clearsky()

    # Final comparison
    print()
    print("=" * 90)
    print("FINAL COMPARISON - FEBRUARY 14, 2026")
    print("=" * 90)
    print()

    if pvgis_success:
        print("PVGIS TMY Data (Most Realistic):")
        print(f"  Daily Energy: {pvgis_kwh:.2f} kWh")
        print(f"  Peak Power: {pvgis_peak/1000:.2f} kW")
        print()

    print("Clear-Sky Model Scenarios:")
    for scenario_name, result in clearsky_results.items():
        print(f"  {scenario_name.replace('_', ' ').title():20}: {result['energy_kwh']:>6.2f} kWh")
    print()

    print("Expected Range for February in Prague (14 kWp system):")
    print("  Clear Day: 10-15 kWh")
    print("  Partly Cloudy: 5-10 kWh")
    print("  Overcast: 2-5 kWh")
    print()

    print("INTERPRETATION:")
    if pvgis_success:
        if pvgis_kwh > 10:
            print(f"  ✓ PVGIS result ({pvgis_kwh:.1f} kWh) suggests a good/clear day")
        elif pvgis_kwh > 5:
            print(f"  ✓ PVGIS result ({pvgis_kwh:.1f} kWh) suggests normal/partly cloudy")
        else:
            print(f"  ✓ PVGIS result ({pvgis_kwh:.1f} kWh) suggests poor/overcast day")
    else:
        print("  ⚠ No PVGIS data available - using clear-sky scenarios")
        print("  Real performance will depend on actual cloud cover and weather")

    print()
    print("=" * 90)
    print("SIMULATION COMPLETE")
    print("=" * 90)


if __name__ == "__main__":
    main()
