"""
Real-World Prague PV System - Today's Test (January 24, 2026)

This script tests the current implementation using your actual system parameters.
Tests both clear-sky (theoretical) and prepares for real weather integration.
"""

from datetime import datetime, timedelta
import pytz
import pandas as pd

from pvsolarsim import Location, PVSystem, calculate_power, simulate_annual


def print_separator(title=""):
    """Print a formatted separator."""
    if title:
        print(f"\n{'=' * 90}")
        print(f"  {title}")
        print(f"{'=' * 90}\n")
    else:
        print("=" * 90)


def main():
    print_separator("REAL-WORLD PV SYSTEM TEST - January 24, 2026")
    print("System: 14.04 kWp Installation in Prague, Czech Republic")
    print(f"Test Date: {datetime.now(pytz.timezone('Europe/Prague')).strftime('%B %d, %Y %H:%M %Z')}")
    print()

    # ==================================================================================
    # SYSTEM CONFIGURATION (Your Real Parameters)
    # ==================================================================================

    location = Location(
        latitude=50.0807494,
        longitude=14.8594164,
        altitude=220,
        timezone="Europe/Prague",
    )

    # Real system parameters
    munchen_panels = {
        'count': 16,
        'power_wp': 450,
        'efficiency': 0.2037,
        'temp_coeff': -0.0035,
        'area_m2': 2.108 * 1.048,
    }

    canadian_panels = {
        'count': 18,
        'power_wp': 380,
        'efficiency': 0.205,
        'temp_coeff': -0.0037,
        'area_m2': 1.765 * 1.048,
    }

    # Calculate totals
    total_power_wp = (
        munchen_panels['count'] * munchen_panels['power_wp'] +
        canadian_panels['count'] * canadian_panels['power_wp']
    )
    total_area_m2 = (
        munchen_panels['count'] * munchen_panels['area_m2'] +
        canadian_panels['count'] * canadian_panels['area_m2']
    )
    weighted_efficiency = total_power_wp / (total_area_m2 * 1000)
    weighted_temp_coeff = (
        (munchen_panels['count'] * munchen_panels['power_wp'] * munchen_panels['temp_coeff'] +
         canadian_panels['count'] * canadian_panels['power_wp'] * canadian_panels['temp_coeff']) /
        total_power_wp
    )

    system = PVSystem(
        panel_area=total_area_m2,
        panel_efficiency=weighted_efficiency,
        tilt=35.0,
        azimuth=202.0,
        temp_coefficient=weighted_temp_coeff,
    )

    print("SYSTEM CONFIGURATION:")
    print(f"  Location: Prague ({location.latitude:.6f}°N, {location.longitude:.6f}°E)")
    print(f"  Altitude: {location.altitude}m")
    print(f"  Total Capacity: {total_power_wp / 1000:.2f} kWp")
    print(f"  - München panels: {munchen_panels['count']} × {munchen_panels['power_wp']}W")
    print(f"  - Canadian panels: {canadian_panels['count']} × {canadian_panels['power_wp']}W")
    print(f"  Panel Area: {total_area_m2:.2f} m²")
    print(f"  Efficiency: {weighted_efficiency * 100:.2f}%")
    print(f"  Temperature Coefficient: {weighted_temp_coeff * 100:.2f}%/°C")
    print(f"  Orientation: {system.tilt}° tilt, {system.azimuth}° azimuth (SSW)")
    print()

    # ==================================================================================
    # TEST 1: INSTANTANEOUS POWER CALCULATION (RIGHT NOW)
    # ==================================================================================

    print_separator("TEST 1: Instantaneous Power (Current Moment)")

    prague_tz = pytz.timezone("Europe/Prague")
    now = datetime.now(prague_tz)
    
    # Typical January conditions in Prague
    winter_conditions = {
        'ambient_temp': 2.0,  # °C (typical January)
        'wind_speed': 3.5,    # m/s (moderate)
        'cloud_cover': 75,    # % (mostly cloudy - typical winter)
    }

    print(f"Timestamp: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Weather Conditions (Typical January):")
    print(f"  - Ambient Temperature: {winter_conditions['ambient_temp']}°C")
    print(f"  - Wind Speed: {winter_conditions['wind_speed']} m/s")
    print(f"  - Cloud Cover: {winter_conditions['cloud_cover']}%")
    print()

    result = calculate_power(
        location=location,
        system=system,
        timestamp=now,
        ambient_temp=winter_conditions['ambient_temp'],
        wind_speed=winter_conditions['wind_speed'],
        cloud_cover=winter_conditions['cloud_cover'],
        soiling_factor=0.95,  # Slight winter soiling
        inverter_efficiency=0.97,
    )

    print("INSTANTANEOUS POWER OUTPUT:")
    print(f"  DC Power: {result.power_w:.2f} W ({result.power_w / 1000:.3f} kW)")
    print(f"  AC Power: {result.power_ac_w:.2f} W ({result.power_ac_w / 1000:.3f} kW)")
    print()
    print("INTERMEDIATE VALUES:")
    print(f"  Solar Elevation: {result.solar_elevation:.2f}°")
    print(f"  Solar Azimuth: {result.solar_azimuth:.2f}°")
    print(f"  Clear-Sky GHI: {result.ghi:.2f} W/m²")
    print(f"  Actual GHI (with clouds): {result.ghi * (1 - winter_conditions['cloud_cover']/100 * 0.75):.2f} W/m²")
    print(f"  POA Irradiance: {result.poa_irradiance:.2f} W/m²")
    print(f"  Cell Temperature: {result.cell_temperature:.2f}°C")
    print(f"  Temperature Factor: {result.temperature_factor:.4f}")
    print()

    # ==================================================================================
    # TEST 2: TODAY'S FULL DAY SIMULATION
    # ==================================================================================

    print_separator("TEST 2: Full Day Simulation (January 24, 2026)")

    # Create time range for today
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    print(f"Simulating: {today_start.strftime('%Y-%m-%d')} (full 24 hours)")
    print(f"Interval: 15 minutes ({96} data points)")
    print()

    # Generate hourly data for today
    times = pd.date_range(
        start=today_start,
        end=today_end,
        freq='15min',
        tz=prague_tz,
        inclusive='left'
    )

    print(f"Calculating {len(times)} timesteps...")
    
    # Calculate power for each timestep
    power_series = []
    for timestamp in times:
        result = calculate_power(
            location=location,
            system=system,
            timestamp=timestamp,
            ambient_temp=winter_conditions['ambient_temp'],
            wind_speed=winter_conditions['wind_speed'],
            cloud_cover=winter_conditions['cloud_cover'],
            soiling_factor=0.95,
            inverter_efficiency=0.97,
        )
        power_series.append({
            'timestamp': timestamp,
            'power_dc_w': result.power_w,
            'power_ac_w': result.power_ac_w,
            'solar_elevation': result.solar_elevation,
            'poa_irradiance': result.poa_irradiance,
        })

    df = pd.DataFrame(power_series)
    df['power_dc_kw'] = df['power_dc_w'] / 1000
    df['power_ac_kw'] = df['power_ac_w'] / 1000

    # Calculate daily statistics
    interval_hours = 0.25  # 15 minutes
    daily_energy_dc = df['power_dc_kw'].sum() * interval_hours
    daily_energy_ac = df['power_ac_kw'].sum() * interval_hours
    peak_power_dc = df['power_dc_kw'].max()
    peak_power_ac = df['power_ac_kw'].max()
    peak_time = df.loc[df['power_dc_kw'].idxmax(), 'timestamp']

    print("\nTODAY'S ENERGY PRODUCTION:")
    print(f"  DC Energy: {daily_energy_dc:.2f} kWh")
    print(f"  AC Energy: {daily_energy_ac:.2f} kWh")
    print(f"  Peak DC Power: {peak_power_dc:.2f} kW at {peak_time.strftime('%H:%M')}")
    print(f"  Peak AC Power: {peak_power_ac:.2f} kW")
    print(f"  Capacity Factor: {(daily_energy_dc / (total_power_wp/1000 * 24)) * 100:.2f}%")
    print()

    # Show hourly breakdown (production hours only)
    production_df = df[df['power_dc_kw'] > 0.1].copy()
    if len(production_df) > 0:
        production_df['hour'] = production_df['timestamp'].dt.hour
        hourly = production_df.groupby('hour').agg({
            'power_dc_kw': 'mean',
            'solar_elevation': 'mean',
            'poa_irradiance': 'mean'
        }).round(2)
        
        print("HOURLY BREAKDOWN (Production Hours):")
        print(f"{'Hour':<6} {'Avg Power':<12} {'Solar Elev':<13} {'POA Irrad':<12}")
        print(f"{'':.<6} {'(kW)':.<12} {'(degrees)':.<13} {'(W/m²)':.<12}")
        for hour, row in hourly.iterrows():
            print(f"{hour:02d}:00  {row['power_dc_kw']:>6.2f} kW    {row['solar_elevation']:>6.2f}°       {row['poa_irradiance']:>6.0f} W/m²")
        print()
    else:
        print("No significant production (nighttime or very low light conditions)")
        print()

    # ==================================================================================
    # TEST 3: COMPARISON WITH CLEAR-SKY (BEST CASE)
    # ==================================================================================

    print_separator("TEST 3: Comparison with Clear-Sky (Best Case Scenario)")

    print("Calculating clear-sky production (0% cloud cover)...")
    
    power_clearsky = []
    for timestamp in times:
        result = calculate_power(
            location=location,
            system=system,
            timestamp=timestamp,
            ambient_temp=winter_conditions['ambient_temp'],
            wind_speed=winter_conditions['wind_speed'],
            cloud_cover=0,  # Clear sky!
            soiling_factor=1.0,  # Clean panels
            inverter_efficiency=0.97,
        )
        power_clearsky.append(result.power_w / 1000)

    daily_energy_clearsky = sum(power_clearsky) * interval_hours

    print("\nCLEAR-SKY COMPARISON:")
    print(f"  Actual (75% clouds): {daily_energy_ac:.2f} kWh AC")
    print(f"  Clear-sky (0% clouds): {daily_energy_clearsky:.2f} kWh DC")
    print(f"  Ratio: {(daily_energy_ac / daily_energy_clearsky) * 100:.1f}% of clear-sky potential")
    print()
    print("Note: Clear-sky represents theoretical maximum for this date.")
    print("      Actual production depends heavily on real cloud cover and weather.")
    print()

    # ==================================================================================
    # INFORMATION ABOUT REAL WEATHER DATA
    # ==================================================================================

    print_separator("NEXT STEP: Real Weather Data Integration")

    print("⚠️  CURRENT LIMITATION:")
    print("This simulation uses ESTIMATED weather conditions (typical January).")
    print()
    print("FOR ACCURATE PREDICTIONS, you need REAL weather data:")
    print()
    print("Option 1: Visual Crossing Weather API (Recommended)")
    print("  - Free tier: 1,000 calls/day")
    print("  - Historical + Forecast data")
    print("  - Global coverage")
    print("  - Sign up: https://www.visualcrossing.com/weather-api")
    print()
    print("Option 2: PVGIS (Free, Europe/Africa/Asia)")
    print("  - No API key needed")
    print("  - TMY (Typical Meteorological Year) data")
    print("  - Already integrated in pvsolarsim")
    print()
    print("Option 3: CSV file with your local data")
    print("  - Export from your weather station")
    print("  - Or download from local meteorological service")
    print()
    print("To use real weather, update the simulate_annual() call:")
    print("  weather_source='visual_crossing'  # Requires API key")
    print("  weather_source='pvgis'            # Free, no key needed")
    print("  weather_source='csv'              # Your data file")
    print()

    print_separator()
    print("✅ Test completed successfully!")
    print()
    print("SUMMARY:")
    print(f"  - Current time power: {result.power_ac_w / 1000:.2f} kW AC")
    print(f"  - Today's production: {daily_energy_ac:.2f} kWh AC (estimated)")
    print(f"  - Peak power today: {peak_power_ac:.2f} kW AC at {peak_time.strftime('%H:%M')}")
    print()
    print("Want real weather data? Let me know if you have an API key!")
    print()


if __name__ == "__main__":
    main()
