"""Example: Using Visual Crossing Weather API with PVSolarSim.

This example demonstrates how to use the Visual Crossing Weather API
to fetch real weather data for solar energy simulations.

Visual Crossing provides:
- Historical weather data (1970-present)
- 15-day weather forecast
- Global coverage
- Solar radiation data (GHI)
- Free tier: 1000 API calls per day

To run this example:
1. Sign up for a free API key at https://www.visualcrossing.com/weather-api
2. Set your API key as an environment variable:
   export VISUAL_CROSSING_API_KEY=your_key_here
3. Run the script:
   python visual_crossing_example.py
"""

import os
import sys
from datetime import datetime, timedelta

import pytz

# Ensure pvsolarsim is in the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pvsolarsim import Location, PVSystem, simulate_annual
from pvsolarsim.weather import VisualCrossingClient


def example_1_fetch_historical_data():
    """Example 1: Fetch historical weather data from Visual Crossing."""
    print("\n" + "=" * 80)
    print("Example 1: Visual Crossing API - Historical Weather Data")
    print("=" * 80 + "\n")

    # Get API key from environment variable
    api_key = os.getenv("VISUAL_CROSSING_API_KEY")
    if not api_key:
        print("⚠️  SKIPPED: VISUAL_CROSSING_API_KEY environment variable not set")
        print("   To run this example, set your API key:")
        print("   export VISUAL_CROSSING_API_KEY=your_key_here")
        print("   Get a free API key at: https://www.visualcrossing.com/weather-api")
        return

    # Create Visual Crossing client
    client = VisualCrossingClient(
        api_key=api_key,
        cache_ttl=3600,  # Cache for 1 hour
        timeout=60,  # 60 second timeout
    )

    # Define location (Boulder, CO)
    latitude = 40.0
    longitude = -105.0

    # Fetch last week's weather data
    end = datetime.now(pytz.UTC)
    start = end - timedelta(days=7)

    print("Fetching historical weather data from Visual Crossing...")
    print(f"Location: {latitude}°N, {longitude}°W (Boulder, CO)")
    print(f"Time range: {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}\n")

    try:
        weather_data = client.read(
            latitude=latitude, longitude=longitude, start=start, end=end
        )

        print("✅ Weather data fetched successfully!")
        print(f"Data points: {len(weather_data)}")
        print(f"Columns: {list(weather_data.columns)}")
        print("\nSample data (first 24 hours):")
        print(weather_data.head(24))
        print("\nData summary:")
        print(weather_data.describe())

        # Analyze the data
        print("\n📊 Data Analysis:")
        print(f"   Average GHI: {weather_data['ghi'].mean():.2f} W/m²")
        print(f"   Max GHI: {weather_data['ghi'].max():.2f} W/m²")
        print(f"   Average temperature: {weather_data['temp_air'].mean():.2f} °C")
        print(f"   Average wind speed: {weather_data['wind_speed'].mean():.2f} m/s")
        print(f"   Average cloud cover: {weather_data['cloud_cover'].mean():.1f}%")

        # Daily statistics
        print("\n📅 Daily Average GHI:")
        if hasattr(weather_data.index, "date"):
            daily_ghi = weather_data.groupby(weather_data.index.date)["ghi"].mean()
            for date, ghi in daily_ghi.items():
                print(f"   {date}: {ghi:6.2f} W/m²")

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        print("   This could be due to:")
        print("   - Invalid API key")
        print("   - API rate limits (free tier: 1000 calls/day)")
        print("   - Network connectivity issues")


def example_2_fetch_forecast():
    """Example 2: Fetch weather forecast from Visual Crossing."""
    print("\n" + "=" * 80)
    print("Example 2: Visual Crossing API - Weather Forecast")
    print("=" * 80 + "\n")

    api_key = os.getenv("VISUAL_CROSSING_API_KEY")
    if not api_key:
        print("⚠️  SKIPPED: VISUAL_CROSSING_API_KEY environment variable not set")
        return

    # Create Visual Crossing client
    client = VisualCrossingClient(api_key=api_key)

    # Define location (Prague, Czech Republic)
    latitude = 50.0
    longitude = 14.4

    print("Fetching 7-day weather forecast from Visual Crossing...")
    print(f"Location: {latitude}°N, {longitude}°E (Prague, Czech Republic)\n")

    try:
        forecast_data = client.read_forecast(latitude=latitude, longitude=longitude, days=7)

        print("✅ Forecast data fetched successfully!")
        print(f"Data points: {len(forecast_data)} hourly forecasts")
        print(f"Forecast range: {forecast_data.index[0]} to {forecast_data.index[-1]}")
        print("\nSample forecast (next 24 hours):")
        print(forecast_data.head(24))

        # Analyze forecast
        print("\n📊 Forecast Analysis:")
        print(f"   Average GHI: {forecast_data['ghi'].mean():.2f} W/m²")
        print(f"   Peak GHI: {forecast_data['ghi'].max():.2f} W/m²")
        print(f"   Average temperature: {forecast_data['temp_air'].mean():.2f} °C")
        print(
            f"   Average cloud cover: {forecast_data['cloud_cover'].mean():.1f}%"
        )

    except Exception as e:
        print(f"❌ Error fetching forecast: {e}")


def example_3_annual_simulation():
    """Example 3: Run annual simulation using Visual Crossing historical data."""
    print("\n" + "=" * 80)
    print("Example 3: Annual Simulation with Visual Crossing Data")
    print("=" * 80 + "\n")

    api_key = os.getenv("VISUAL_CROSSING_API_KEY")
    if not api_key:
        print("⚠️  SKIPPED: VISUAL_CROSSING_API_KEY environment variable not set")
        return

    # Define location and system
    location = Location(
        latitude=40.0, longitude=-105.0, altitude=1655, timezone="America/Denver"
    )

    system = PVSystem(
        panel_area=20.0,  # 20 m²
        panel_efficiency=0.20,  # 20%
        tilt=35,  # Tilted 35° from horizontal
        azimuth=180,  # South-facing
        temp_coefficient=-0.004,  # -0.4%/°C
    )

    print("Location: Boulder, CO (40°N, 105°W)")
    print(f"System: {system.panel_area} m² @ {system.panel_efficiency*100}% efficiency")
    print(f"Tilt: {system.tilt}°, Azimuth: {system.azimuth}° (South)\n")

    # Note: For a full annual simulation, you would fetch the entire year
    # Here we demonstrate with recent data (last 30 days) to stay within free tier
    print("Fetching last 30 days of weather data...")
    print("(For full annual simulation, use TMY data or fetch full year)\n")

    try:
        # Create client
        client = VisualCrossingClient(api_key=api_key)

        # Fetch recent data
        end = datetime.now(pytz.UTC)
        start = end - timedelta(days=30)

        weather_data = client.read(
            latitude=location.latitude,
            longitude=location.longitude,
            start=start,
            end=end,
        )

        print(f"✅ Fetched {len(weather_data)} hours of weather data")

        # For this example, we'll calculate statistics directly
        # rather than using simulate_annual (which expects a full year)
        print("\n📊 Weather Data Summary:")
        print(f"   Average GHI: {weather_data['ghi'].mean():.2f} W/m²")
        print(f"   Total solar energy: {weather_data['ghi'].sum() / 1000:.2f} kWh/m²")
        print(f"   Average temperature: {weather_data['temp_air'].mean():.2f} °C")

        # Note about full annual simulation
        print("\n💡 Note for Full Annual Simulation:")
        print("   To run a full year simulation with Visual Crossing:")
        print("   1. Fetch data for the entire year (365 days)")
        print("   2. Free tier allows 1000 calls/day, so you can get ~1000 hours/call")
        print("   3. Or use TMY data from PVGIS for typical year analysis")
        print("   4. Pass weather_data to simulate_annual() function")

    except Exception as e:
        print(f"❌ Error running simulation: {e}")


def example_4_compare_with_pvgis():
    """Example 4: Compare Visual Crossing data with PVGIS."""
    print("\n" + "=" * 80)
    print("Example 4: Comparing Visual Crossing with PVGIS")
    print("=" * 80 + "\n")

    api_key = os.getenv("VISUAL_CROSSING_API_KEY")
    if not api_key:
        print("⚠️  SKIPPED: VISUAL_CROSSING_API_KEY environment variable not set")
        return

    try:
        from pvsolarsim.weather import PVGISClient

        # Define location
        latitude = 45.0
        longitude = 8.0

        print("Comparing weather data sources for Milan, Italy")
        print(f"Location: {latitude}°N, {longitude}°E\n")

        # Fetch PVGIS TMY data
        print("1. Fetching PVGIS Typical Meteorological Year (TMY) data...")
        pvgis_client = PVGISClient()
        pvgis_data = pvgis_client.read_tmy(latitude=latitude, longitude=longitude)
        print(f"   ✅ PVGIS: {len(pvgis_data)} hourly records (typical year)")

        # Fetch Visual Crossing recent data
        print("2. Fetching Visual Crossing historical data (last 7 days)...")
        vc_client = VisualCrossingClient(api_key=api_key)
        end = datetime.now(pytz.UTC)
        start = end - timedelta(days=7)
        vc_data = vc_client.read(latitude=latitude, longitude=longitude, start=start, end=end)
        print(f"   ✅ Visual Crossing: {len(vc_data)} hourly records (recent)")

        # Compare statistics
        print("\n📊 Comparison:")
        print(f"\n{'Metric':<25} {'PVGIS TMY':>15} {'Visual Crossing':>18}")
        print("-" * 60)
        print(
            f"{'Average GHI (W/m²)':<25} {pvgis_data['ghi'].mean():>15.2f} {vc_data['ghi'].mean():>18.2f}"
        )
        print(
            f"{'Max GHI (W/m²)':<25} {pvgis_data['ghi'].max():>15.2f} {vc_data['ghi'].max():>18.2f}"
        )
        print(
            f"{'Avg Temperature (°C)':<25} {pvgis_data['temp_air'].mean():>15.2f} {vc_data['temp_air'].mean():>18.2f}"
        )
        print(
            f"{'Avg Wind Speed (m/s)':<25} {pvgis_data['wind_speed'].mean():>15.2f} {vc_data['wind_speed'].mean():>18.2f}"
        )

        print("\n💡 Interpretation:")
        print("   - PVGIS TMY: Typical year based on long-term averages")
        print("   - Visual Crossing: Actual recent weather conditions")
        print("   - Use PVGIS for long-term energy predictions")
        print("   - Use Visual Crossing for real-time analysis and validation")

    except Exception as e:
        print(f"❌ Error in comparison: {e}")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("PVSolarSim - Visual Crossing Weather API Examples")
    print("=" * 80)

    # Check for API key
    api_key = os.getenv("VISUAL_CROSSING_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: VISUAL_CROSSING_API_KEY not set!")
        print("Most examples will be skipped.\n")
        print("To run these examples:")
        print("1. Sign up for a free API key at:")
        print("   https://www.visualcrossing.com/weather-api")
        print("2. Set the environment variable:")
        print("   export VISUAL_CROSSING_API_KEY=your_key_here")
        print("3. Run this script again\n")

    # Run examples
    example_1_fetch_historical_data()
    example_2_fetch_forecast()
    example_3_annual_simulation()
    example_4_compare_with_pvgis()

    print("\n" + "=" * 80)
    print("Examples completed!")
    print("=" * 80 + "\n")

    print("📝 Summary:")
    print("   ✅ Example 1: Fetch historical weather data")
    print("   ✅ Example 2: Fetch weather forecast")
    print("   ✅ Example 3: Annual simulation with real data")
    print("   ✅ Example 4: Compare Visual Crossing with PVGIS")

    print("\n💡 Key Features of Visual Crossing:")
    print("   - Free tier: 1000 API calls per day")
    print("   - Global coverage with historical data (1970-present)")
    print("   - 15-day weather forecast")
    print("   - Solar radiation data (GHI)")
    print("   - Hourly data resolution")
    print("   - No credit card required for free tier")

    print("\n📚 Next Steps:")
    print("   - Get your free API key at visualcrossing.com")
    print("   - Explore different locations and time periods")
    print("   - Integrate with your PV system simulations")
    print("   - Compare with PVGIS TMY data for validation\n")


if __name__ == "__main__":
    main()
