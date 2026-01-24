"""
Real-World Prague PV System - Today with PVGIS Weather Data
January 24, 2026

This script uses PVGIS (free European weather database) for realistic weather.
No API key required!
"""

from datetime import datetime
import pytz

from pvsolarsim import Location, PVSystem, simulate_annual


def main():
    print("=" * 90)
    print("REAL-WORLD PV SYSTEM: Today's Performance with PVGIS Weather Data")
    print("14.04 kWp System in Prague, Czech Republic")
    print(f"Date: {datetime.now(pytz.timezone('Europe/Prague')).strftime('%B %d, %Y %H:%M %Z')}")
    print("=" * 90)
    print()

    # System configuration (your real parameters)
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

    print("System Configuration:")
    print(f"  Location: Prague ({location.latitude}°N, {location.longitude}°E, {location.altitude}m)")
    print(f"  Total Capacity: {total_power_wp / 1000:.2f} kWp")
    print(f"  Panel Area: {total_area_m2:.2f} m²")
    print(f"  Efficiency: {weighted_efficiency * 100:.2f}%")
    print(f"  Orientation: {system.tilt}° tilt, {system.azimuth}° azimuth (SSW)")
    print()

    print("=" * 90)
    print("Fetching weather data from PVGIS...")
    print("=" * 90)
    print()
    print("PVGIS provides Typical Meteorological Year (TMY) data for Europe.")
    print("This represents average weather conditions based on historical data.")
    print()

    try:
        # Simulate with PVGIS data
        print("Running annual simulation with PVGIS TMY data...")
        print("(This will take a moment to fetch data from PVGIS API...)")
        print()
        
        results = simulate_annual(
            location=location,
            system=system,
            year=2025,  # PVGIS uses TMY data, year doesn't matter
            interval_minutes=60,
            weather_source='pvgis',
            soiling_factor=0.95,
            inverter_efficiency=0.97,
        )

        print("✅ Simulation completed successfully!")
        print()
        print("=" * 90)
        print("ANNUAL PRODUCTION (PVGIS TMY Data)")
        print("=" * 90)
        print()
        print(f"Annual Energy Production: {results.statistics.total_energy_kwh:.2f} kWh AC")
        print(f"Specific Yield: {results.statistics.total_energy_kwh / (total_power_wp/1000):.0f} kWh/kWp")
        print(f"Capacity Factor: {results.statistics.capacity_factor * 100:.2f}%")
        print(f"Peak Power: {results.statistics.peak_power_w / 1000:.2f} kW")
        print(f"Average Daily: {results.statistics.total_energy_kwh / 365:.2f} kWh")
        print()

        # Monthly breakdown
        print("=" * 90)
        print("MONTHLY BREAKDOWN")
        print("=" * 90)
        print()
        monthly = results.get_monthly_summary()
        print(f"{'Month':<12} {'Energy (kWh)':<15} {'Daily Avg (kWh)':<18} {'Peak Power (kW)':<15}")
        print("-" * 90)
        for _, row in monthly.iterrows():
            month_name = row['month'].strftime('%B %Y')
            print(f"{month_name:<12} {row['total_energy_kwh']:>10.1f}     "
                  f"{row['avg_daily_kwh']:>10.2f}         {row['peak_power_kw']:>10.2f}")
        print()

        # Today's expected production (January average)
        jan_data = monthly[monthly['month'].dt.month == 1]
        if not jan_data.empty:
            jan_daily_avg = jan_data.iloc[0]['avg_daily_kwh']
            print("=" * 90)
            print("TODAY'S EXPECTED PRODUCTION (January Average from PVGIS)")
            print("=" * 90)
            print()
            print(f"Expected production: {jan_daily_avg:.2f} kWh AC")
            print(f"(Based on typical January weather in Prague)")
            print()

        print("✅ SUCCESS: Real weather data integration working!")
        print()
        print("Note: PVGIS provides historical average conditions (TMY).")
        print("      For TODAY's actual weather, use Visual Crossing or local data.")
        print()

    except Exception as e:
        print(f"❌ Error fetching PVGIS data: {e}")
        print()
        print("This could be due to:")
        print("  - Network connection issues")
        print("  - PVGIS API temporarily unavailable")
        print("  - Location outside PVGIS coverage")
        print()
        print("Falling back to clear-sky simulation...")
        print()

        # Fallback to clear-sky
        results = simulate_annual(
            location=location,
            system=system,
            year=2025,
            interval_minutes=60,
            weather_source='clear_sky',
            ambient_temp=10.0,
            wind_speed=2.5,
            cloud_cover=0,
        )

        print(f"Clear-sky annual production: {results.statistics.total_energy_kwh:.2f} kWh")
        print("(This is theoretical maximum, not realistic)")
        print()


if __name__ == "__main__":
    main()
