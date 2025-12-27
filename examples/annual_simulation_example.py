#!/usr/bin/env python3
"""Example: Annual PV energy production simulation.

This example demonstrates how to use PVSolarSim to simulate a full year
of PV energy production with clear-sky conditions.
"""

from pvsolarsim import Location, PVSystem, simulate_annual


def main():
    """Run annual simulation examples."""
    # Define location (Boulder, Colorado)
    location = Location(
        latitude=40.0,
        longitude=-105.0,
        altitude=1655,  # meters
        timezone="America/Denver",
    )

    # Define PV system
    # 20 m² of panels with 20% efficiency
    # Tilted at 35° (good for 40°N latitude)
    # Facing south (azimuth 180°)
    system = PVSystem(
        panel_area=20.0,  # m²
        panel_efficiency=0.20,  # 20%
        tilt=35.0,  # degrees
        azimuth=180.0,  # degrees (south)
        temp_coefficient=-0.004,  # -0.4%/°C
    )

    print("=" * 70)
    print("Annual PV Energy Production Simulation")
    print("=" * 70)
    print(f"\nLocation: Boulder, Colorado ({location.latitude}°N, {location.longitude}°W)")
    print(f"Altitude: {location.altitude} m")
    print("\nSystem Configuration:")
    print(f"  Panel area: {system.panel_area} m²")
    print(f"  Efficiency: {system.panel_efficiency * 100}%")
    print(f"  Tilt: {system.tilt}°")
    print(f"  Azimuth: {system.azimuth}°")
    print(f"  Temperature coefficient: {system.temp_coefficient * 100}%/°C")

    # Example 1: Basic annual simulation with clear sky
    print("\n" + "-" * 70)
    print("Example 1: Clear Sky Simulation (5-minute intervals)")
    print("-" * 70)

    results = simulate_annual(
        location=location,
        system=system,
        year=2025,
        interval_minutes=5,  # 5-minute intervals
        weather_source="clear_sky",
    )

    print("\nAnnual Performance:")
    print(f"  Total energy: {results.statistics.total_energy_kwh:.2f} kWh")
    print(f"  Capacity factor: {results.statistics.capacity_factor * 100:.2f}%")
    print(f"  Peak power: {results.statistics.peak_power_w:.0f} W")
    print(f"  Average power (daylight): {results.statistics.average_power_w:.0f} W")
    print(f"  Performance ratio: {results.statistics.performance_ratio:.2%}")
    print(f"  Total daylight hours: {results.statistics.total_daylight_hours:.1f} h")

    print("\nMonthly Energy Production:")
    for month, energy in results.statistics.monthly_energy_kwh.items():
        print(f"  {month}: {energy:.2f} kWh")

    # Example 2: With cloud cover
    print("\n" + "-" * 70)
    print("Example 2: With Cloud Cover (30% average)")
    print("-" * 70)

    results_cloudy = simulate_annual(
        location=location,
        system=system,
        year=2025,
        interval_minutes=60,  # Hourly for speed
        cloud_cover=30,  # 30% cloud cover
    )

    print("\nAnnual Performance:")
    print(f"  Total energy: {results_cloudy.statistics.total_energy_kwh:.2f} kWh")
    print(f"  Capacity factor: {results_cloudy.statistics.capacity_factor * 100:.2f}%")
    print(f"  Energy reduction vs clear: {(1 - results_cloudy.statistics.total_energy_kwh / results.statistics.total_energy_kwh) * 100:.1f}%")

    # Example 3: With soiling and degradation
    print("\n" + "-" * 70)
    print("Example 3: With Soiling and Degradation")
    print("-" * 70)

    results_real = simulate_annual(
        location=location,
        system=system,
        year=2025,
        interval_minutes=60,
        soiling_factor=0.98,  # 2% soiling loss
        degradation_factor=0.99,  # 1% degradation (1 year old)
    )

    print("\nAnnual Performance:")
    print(f"  Total energy: {results_real.statistics.total_energy_kwh:.2f} kWh")
    print(f"  Total losses: {(1 - results_real.statistics.total_energy_kwh / results.statistics.total_energy_kwh) * 100:.1f}%")

    # Example 4: With inverter efficiency (AC power)
    print("\n" + "-" * 70)
    print("Example 4: AC Power Output (with inverter)")
    print("-" * 70)

    results_ac = simulate_annual(
        location=location,
        system=system,
        year=2025,
        interval_minutes=60,
        inverter_efficiency=0.96,  # 96% inverter efficiency
    )

    dc_energy = results_ac.time_series["power_w"].sum() * 60 / 60000  # Convert to kWh
    ac_energy = results_ac.time_series["power_ac_w"].sum() * 60 / 60000

    print("\nAnnual Performance:")
    print(f"  DC energy: {dc_energy:.2f} kWh")
    print(f"  AC energy: {ac_energy:.2f} kWh")
    print(f"  Inverter efficiency (actual): {(ac_energy / dc_energy) * 100:.2f}%")

    # Export results
    print("\n" + "-" * 70)
    print("Example 5: Export Results")
    print("-" * 70)

    output_file = "annual_production_2025.csv"
    results.export_csv(output_file)
    print(f"\nTime series data exported to: {output_file}")
    print(f"  Total rows: {len(results.time_series)}")
    print(f"  Columns: {', '.join(results.time_series.columns)}")

    # Show monthly summary
    print("\n" + "-" * 70)
    print("Monthly Summary")
    print("-" * 70)

    monthly = results.get_monthly_summary()
    print(f"\n{monthly}")

    print("\n" + "=" * 70)
    print("Simulation Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
