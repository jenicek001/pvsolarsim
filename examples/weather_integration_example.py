"""Example: Using weather data with PVSolarSim.

This example demonstrates how to use various weather data sources
with the annual simulation.
"""

import tempfile
from pathlib import Path

import pandas as pd

from pvsolarsim import Location, PVSystem, simulate_annual


def example_1_csv_weather_data():
    """Example 1: Using weather data from CSV file."""
    print("\n=== Example 1: CSV Weather Data ===\n")

    # Create a sample CSV file with weather data
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "weather.csv"

        # Generate sample weather data for a week
        timestamps = pd.date_range(
            "2025-01-01", periods=168, freq="H", tz="America/Denver"
        )

        # Simulate realistic weather patterns
        hours = timestamps.hour.values
        ghi_values = [max(0, 800 * abs(1 - abs(h - 12) / 12) ** 2) for h in hours]

        weather_data = pd.DataFrame(
            {
                "timestamp": timestamps,
                "ghi": ghi_values,
                "dni": [g * 1.2 for g in ghi_values],
                "dhi": [g * 0.3 for g in ghi_values],
                "temp_air": [15 + 10 * abs(1 - abs(h - 12) / 12) for h in hours],
                "wind_speed": [2.0 + h * 0.1 for h in hours],
                "cloud_cover": [20.0] * len(hours),
            }
        )

        # Save to CSV
        weather_data.to_csv(csv_path, index=False)
        print(f"Created weather CSV: {csv_path}")
        print(f"Sample data:\n{weather_data.head()}\n")

        # Set up location and system
        location = Location(
            latitude=40.0, longitude=-105.0, altitude=1655, timezone="America/Denver"
        )
        system = PVSystem(
            panel_area=20.0,
            panel_efficiency=0.20,
            tilt=35,
            azimuth=180,
            temp_coefficient=-0.004,
        )

        # Run simulation with CSV data
        results = simulate_annual(
            location=location,
            system=system,
            year=2025,
            interval_minutes=60,
            weather_source="csv",
            file_path=str(csv_path),
            soiling_factor=0.98,
            inverter_efficiency=0.96,
        )

        print("Simulation completed!")
        print(f"Total energy: {results.statistics.total_energy_kwh:.2f} kWh")
        print(f"Peak power: {results.statistics.peak_power_w:.2f} W")
        print(f"Capacity factor: {results.statistics.capacity_factor * 100:.2f}%\n")


def example_2_dataframe_weather_data():
    """Example 2: Using weather data from pandas DataFrame."""
    print("\n=== Example 2: DataFrame Weather Data ===\n")

    # Create weather data directly as DataFrame
    timestamps = pd.date_range("2025-06-01", periods=720, freq="H", tz="UTC")

    # Summer weather pattern
    hours = timestamps.hour.values

    ghi_values = [max(0, 900 * abs(1 - abs(h - 12) / 12) ** 2.5) for h in hours]

    weather_df = pd.DataFrame(
        {
            "ghi": ghi_values,
            "dni": [g * 1.3 for g in ghi_values],
            "dhi": [g * 0.25 for g in ghi_values],
            "temp_air": [20 + 15 * abs(1 - abs(h - 14) / 14) for h in hours],
            "wind_speed": [3.0] * len(hours),
        },
        index=timestamps,
    )

    print(f"Weather data shape: {weather_df.shape}")
    print(f"Sample data:\n{weather_df.head()}\n")

    # Set up location and system
    location = Location(latitude=49.8, longitude=15.5, altitude=300, timezone="UTC")
    system = PVSystem(
        panel_area=30.0, panel_efficiency=0.22, tilt=30, azimuth=180
    )

    # Run simulation with DataFrame
    results = simulate_annual(
        location=location,
        system=system,
        year=2025,
        interval_minutes=60,
        weather_source="weather_data",
        weather_data=weather_df,
        soiling_factor=0.99,
    )

    print("Simulation completed!")
    print(f"Total energy: {results.statistics.total_energy_kwh:.2f} kWh")
    print(f"Average power: {results.statistics.average_power_w:.2f} W")
    print(f"Performance ratio: {results.statistics.performance_ratio:.2f}\n")


def example_3_clear_sky_comparison():
    """Example 3: Compare clear sky with cloudy conditions."""
    print("\n=== Example 3: Clear Sky vs Cloudy ===\n")

    location = Location(latitude=45.0, longitude=8.0, altitude=200, timezone="UTC")
    system = PVSystem(panel_area=25.0, panel_efficiency=0.20, tilt=35, azimuth=180)

    # Clear sky simulation
    print("Running clear sky simulation...")
    results_clear = simulate_annual(
        location=location,
        system=system,
        year=2025,
        interval_minutes=60,
        weather_source="clear_sky",
        ambient_temp=25,
        wind_speed=2,
        cloud_cover=0,
    )

    # Cloudy simulation
    print("Running cloudy simulation...")
    results_cloudy = simulate_annual(
        location=location,
        system=system,
        year=2025,
        interval_minutes=60,
        weather_source="clear_sky",
        ambient_temp=25,
        wind_speed=2,
        cloud_cover=40,  # 40% cloud cover
    )

    print("\nClear Sky:")
    print(f"  Total energy: {results_clear.statistics.total_energy_kwh:.2f} kWh")
    print(f"  Capacity factor: {results_clear.statistics.capacity_factor * 100:.2f}%")

    print("\nCloudy (40% cover):")
    print(f"  Total energy: {results_cloudy.statistics.total_energy_kwh:.2f} kWh")
    print(f"  Capacity factor: {results_cloudy.statistics.capacity_factor * 100:.2f}%")

    energy_loss = (
        (results_clear.statistics.total_energy_kwh
         - results_cloudy.statistics.total_energy_kwh)
        / results_clear.statistics.total_energy_kwh
        * 100
    )
    print(f"\nEnergy loss due to clouds: {energy_loss:.1f}%\n")


def example_4_custom_column_mapping():
    """Example 4: CSV with custom column names."""
    print("\n=== Example 4: Custom Column Mapping ===\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "custom_weather.csv"

        # Create CSV with non-standard column names
        timestamps = pd.date_range("2025-03-01", periods=24, freq="H", tz="UTC")
        hours = timestamps.hour.values

        custom_data = pd.DataFrame(
            {
                "datetime": timestamps,
                "global_irradiance": [max(0, 700 * abs(1 - abs(h - 12) / 12) ** 2) for h in hours],
                "temperature_celsius": [12 + 8 * abs(1 - abs(h - 14) / 14) for h in hours],
                "wind_m_s": [4.0] * len(hours),
            }
        )

        custom_data.to_csv(csv_path, index=False)
        print(f"Created custom CSV with columns: {list(custom_data.columns)}\n")

        location = Location(latitude=52.5, longitude=13.4, altitude=50, timezone="UTC")
        system = PVSystem(panel_area=15.0, panel_efficiency=0.19, tilt=40, azimuth=180)

        # Use column mapping to handle custom names
        results = simulate_annual(
            location=location,
            system=system,
            year=2025,
            interval_minutes=60,
            weather_source="csv",
            file_path=str(csv_path),
            column_mapping={
                "timestamp": "datetime",
                "ghi": "global_irradiance",
                "temp_air": "temperature_celsius",
                "wind_speed": "wind_m_s",
            },
        )

        print("Simulation completed with custom column mapping!")
        print(f"Total energy: {results.statistics.total_energy_kwh:.2f} kWh\n")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("PVSolarSim - Weather Data Integration Examples")
    print("=" * 70)

    example_1_csv_weather_data()
    example_2_dataframe_weather_data()
    example_3_clear_sky_comparison()
    example_4_custom_column_mapping()

    print("=" * 70)
    print("All examples completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
