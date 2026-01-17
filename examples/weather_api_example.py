"""Example: Using Weather API Clients with PVSolarSim.

This example demonstrates how to use the OpenWeatherMap and PVGIS API clients
to fetch real weather data for solar energy simulations.

NOTE: This example requires API keys which are not included. To run this example:
1. Sign up for a free API key at https://openweathermap.org/api
2. Set your API key as an environment variable: export OPENWEATHERMAP_API_KEY=your_key_here
3. Run the script: python weather_api_example.py
"""

import os
import sys
from datetime import datetime, timedelta

import pytz

# Ensure pvsolarsim is in the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pvsolarsim import Location, PVSystem, simulate_annual
from pvsolarsim.weather import OpenWeatherMapClient, PVGISClient


def example_1_openweathermap_basic():
    """Example 1: Fetch weather data from OpenWeatherMap API."""
    print("\n" + "=" * 80)
    print("Example 1: OpenWeatherMap API - Basic Usage")
    print("=" * 80 + "\n")

    # Get API key from environment variable
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        print("⚠️  SKIPPED: OPENWEATHERMAP_API_KEY environment variable not set")
        print("   To run this example, set your API key:")
        print("   export OPENWEATHERMAP_API_KEY=your_key_here")
        return

    # Create OpenWeatherMap client
    client = OpenWeatherMapClient(
        api_key=api_key,
        cache_ttl=3600,  # Cache for 1 hour
        timeout=30  # 30 second timeout
    )

    # Define location
    latitude = 40.0  # Boulder, CO
    longitude = -105.0

    # Fetch weather data for the past day
    # NOTE: Free tier has limited historical data
    end = datetime.now(pytz.UTC)
    start = end - timedelta(hours=48)

    print(f"Fetching weather data from OpenWeatherMap...")
    print(f"Location: {latitude}°N, {longitude}°W")
    print(f"Time range: {start} to {end}\n")

    try:
        weather_data = client.read(
            latitude=latitude,
            longitude=longitude,
            start=start,
            end=end
        )

        print("✅ Weather data fetched successfully!")
        print(f"Data points: {len(weather_data)}")
        print(f"Columns: {list(weather_data.columns)}")
        print(f"\nSample data:")
        print(weather_data.head())
        print(f"\nData summary:")
        print(weather_data.describe())

        # Note about limitations
        print("\n⚠️  Note: OpenWeatherMap free tier provides:")
        print("   - Temperature, wind speed, cloud cover")
        print("   - Does NOT include GHI/DNI/DHI (solar irradiance)")
        print("   - For solar simulations, use clear-sky models or PVGIS")

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        print("   This could be due to:")
        print("   - Invalid API key")
        print("   - API rate limits")
        print("   - Network connectivity issues")


def example_2_pvgis_tmy():
    """Example 2: Fetch Typical Meteorological Year (TMY) data from PVGIS."""
    print("\n" + "=" * 80)
    print("Example 2: PVGIS API - Typical Meteorological Year (TMY) Data")
    print("=" * 80 + "\n")

    # Create PVGIS client (no API key required - it's a free service!)
    client = PVGISClient(
        cache_ttl=604800,  # Cache for 7 days (TMY data doesn't change often)
        timeout=60  # PVGIS can be slower, allow 60 seconds
    )

    # Define location (Prague, Czech Republic)
    latitude = 50.0
    longitude = 14.4

    print(f"Fetching TMY data from PVGIS...")
    print(f"Location: {latitude}°N, {longitude}°E")
    print(f"Data type: Typical Meteorological Year (synthesized from historical data)\n")

    try:
        tmy_data = client.read_tmy(latitude=latitude, longitude=longitude)

        print("✅ TMY data fetched successfully!")
        print(f"Data points: {len(tmy_data)}")
        print(f"Columns: {list(tmy_data.columns)}")
        print(f"\nSample data:")
        print(tmy_data.head())
        print(f"\nData summary:")
        print(tmy_data.describe())

        # Analyze the data
        print("\n📊 Data Analysis:")
        print(f"   Average GHI: {tmy_data['ghi'].mean():.2f} W/m²")
        print(f"   Max GHI: {tmy_data['ghi'].max():.2f} W/m²")
        print(f"   Average temperature: {tmy_data['temp_air'].mean():.2f} °C")
        print(f"   Average wind speed: {tmy_data['wind_speed'].mean():.2f} m/s")

        # Monthly statistics
        print("\n📅 Monthly Average GHI:")
        if hasattr(tmy_data.index, 'month'):
            monthly_ghi = tmy_data.groupby(tmy_data.index.month)['ghi'].mean()
            for month, ghi in monthly_ghi.items():
                month_name = datetime(2000, month, 1).strftime("%B")
                print(f"   {month_name:12s}: {ghi:6.2f} W/m²")

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        print("   This could be due to:")
        print("   - Location outside PVGIS coverage area")
        print("   - Network connectivity issues")
        print("   - PVGIS service temporarily unavailable")


def example_3_simulation_with_pvgis():
    """Example 3: Run annual simulation using PVGIS TMY data."""
    print("\n" + "=" * 80)
    print("Example 3: Annual Simulation with PVGIS TMY Data")
    print("=" * 80 + "\n")

    # Define location and system
    location = Location(
        latitude=40.0,
        longitude=-105.0,
        altitude=1655,
        timezone="America/Denver"
    )

    system = PVSystem(
        panel_area=20.0,  # 20 m²
        panel_efficiency=0.20,  # 20%
        tilt=35,  # Tilted 35° from horizontal
        azimuth=180,  # South-facing
        temp_coefficient=-0.004  # -0.4%/°C
    )

    print("Location: Boulder, CO (40°N, 105°W)")
    print(f"System: {system.panel_area} m² @ {system.panel_efficiency*100}% efficiency")
    print(f"Tilt: {system.tilt}°, Azimuth: {system.azimuth}° (South)\n")
    print("Running annual simulation with PVGIS TMY data...")
    print("(This may take a moment as it fetches data from PVGIS...)\n")

    try:
        # Run simulation using PVGIS data
        results = simulate_annual(
            location=location,
            system=system,
            year=2025,
            interval_minutes=60,  # Hourly data
            weather_source="pvgis",  # Use PVGIS TMY data
            soiling_factor=0.98,  # 2% soiling losses
            inverter_efficiency=0.96  # 96% inverter efficiency
        )

        print("✅ Simulation completed successfully!\n")
        print("📊 Annual Energy Production Results:")
        print(f"   Total Energy: {results.statistics.total_energy_kwh:.2f} kWh/year")
        print(f"   Peak Power: {results.statistics.peak_power_w:.2f} W")
        print(f"   Average Power: {results.statistics.average_power_w:.2f} W")
        print(f"   Capacity Factor: {results.statistics.capacity_factor * 100:.2f}%")
        print(f"   Performance Ratio: {results.statistics.performance_ratio:.3f}")

        # Monthly breakdown
        print("\n📅 Monthly Energy Production:")
        monthly = results.monthly_summary()
        for idx, row in monthly.iterrows():
            month_name = idx.strftime("%B %Y")
            print(f"   {month_name:15s}: {row['energy_kwh']:7.2f} kWh")

        # Export results
        output_file = "/tmp/pvgis_simulation_results.csv"
        results.export_csv(output_file)
        print(f"\n💾 Results exported to: {output_file}")

    except Exception as e:
        print(f"❌ Error running simulation: {e}")


def example_4_compare_weather_sources():
    """Example 4: Compare clear-sky vs PVGIS TMY data."""
    print("\n" + "=" * 80)
    print("Example 4: Comparing Clear-Sky Model vs PVGIS TMY Data")
    print("=" * 80 + "\n")

    location = Location(latitude=45.0, longitude=8.0, altitude=200, timezone="UTC")
    system = PVSystem(panel_area=25.0, panel_efficiency=0.20, tilt=35, azimuth=180)

    print("Comparing two simulation scenarios:")
    print("1. Clear-sky model (theoretical maximum)")
    print("2. PVGIS TMY data (realistic with clouds, weather variations)\n")

    try:
        # Scenario 1: Clear-sky
        print("Running clear-sky simulation...")
        results_clearsky = simulate_annual(
            location=location,
            system=system,
            year=2025,
            interval_minutes=60,
            weather_source="clear_sky",
            ambient_temp=15,
            wind_speed=2,
            cloud_cover=0  # Perfect clear sky
        )

        # Scenario 2: PVGIS TMY
        print("Running PVGIS TMY simulation...")
        results_pvgis = simulate_annual(
            location=location,
            system=system,
            year=2025,
            interval_minutes=60,
            weather_source="pvgis"
        )

        print("\n✅ Both simulations completed!\n")
        print("📊 Comparison Results:")
        print(f"\n{'Metric':<25} {'Clear-Sky':>12} {'PVGIS TMY':>12} {'Difference':>12}")
        print("-" * 65)

        energy_cs = results_clearsky.statistics.total_energy_kwh
        energy_pv = results_pvgis.statistics.total_energy_kwh
        diff_energy = ((energy_pv - energy_cs) / energy_cs * 100)

        cf_cs = results_clearsky.statistics.capacity_factor * 100
        cf_pv = results_pvgis.statistics.capacity_factor * 100
        diff_cf = cf_pv - cf_cs

        print(f"{'Annual Energy (kWh)':<25} {energy_cs:>12.1f} {energy_pv:>12.1f} {diff_energy:>11.1f}%")
        print(f"{'Capacity Factor (%)':<25} {cf_cs:>12.2f} {cf_pv:>12.2f} {diff_cf:>11.2f}%")
        print(f"{'Peak Power (W)':<25} {results_clearsky.statistics.peak_power_w:>12.1f} {results_pvgis.statistics.peak_power_w:>12.1f}")

        print("\n💡 Interpretation:")
        if energy_pv < energy_cs:
            reduction = abs(diff_energy)
            print(f"   PVGIS TMY data shows {reduction:.1f}% less energy than clear-sky")
            print("   This is expected due to clouds, weather variations, and atmospheric effects")
            print("   PVGIS data is more realistic for actual system performance")
        else:
            print("   Unexpected result - PVGIS should typically be lower than clear-sky")

    except Exception as e:
        print(f"❌ Error in comparison: {e}")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("PVSolarSim - Weather API Integration Examples")
    print("=" * 80)

    # Run examples
    example_1_openweathermap_basic()
    example_2_pvgis_tmy()
    example_3_simulation_with_pvgis()
    example_4_compare_weather_sources()

    print("\n" + "=" * 80)
    print("Examples completed!")
    print("=" * 80 + "\n")

    print("📝 Summary:")
    print("   ✅ Example 1: OpenWeatherMap basic usage (requires API key)")
    print("   ✅ Example 2: PVGIS TMY data fetching (free, no API key)")
    print("   ✅ Example 3: Annual simulation with PVGIS")
    print("   ✅ Example 4: Comparing weather sources")
    print("\n💡 Next Steps:")
    print("   - Get an OpenWeatherMap API key to enable Example 1")
    print("   - Modify locations and system parameters for your use case")
    print("   - Explore other weather data sources (CSV, JSON files)")
    print("   - Check the documentation for more advanced features\n")


if __name__ == "__main__":
    main()
