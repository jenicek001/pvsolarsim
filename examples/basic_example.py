"""
Example: Basic Solar Position and Irradiance Calculation

This example demonstrates the core functionality of PVSolarSim:
1. Calculate solar position for a specific location and time
2. Calculate clear-sky irradiance using different models
3. Compare results across different conditions
"""

from datetime import datetime

import pytz

from pvsolarsim import Location, PVSystem
from pvsolarsim.atmosphere import ClearSkyModel, calculate_clearsky_irradiance
from pvsolarsim.solar import calculate_solar_position


def main():
    print("=" * 80)
    print("PVSolarSim - Solar Position and Clear-Sky Irradiance Example")
    print("=" * 80)
    print()

    # Define location (Prague, Czech Republic)
    location = Location(
        latitude=49.8, longitude=15.5, altitude=300, timezone="Europe/Prague"
    )

    print(f"Location: {location.latitude}°N, {location.longitude}°E")
    print(f"Altitude: {location.altitude}m")
    print(f"Timezone: {location.timezone}")
    print()

    # Define PV system
    system = PVSystem(
        panel_area=20.0,  # 20 m² of panels
        panel_efficiency=0.20,  # 20% efficiency
        tilt=35.0,  # 35° tilt (optimal for this latitude)
        azimuth=180.0,  # South-facing
        temp_coefficient=-0.004,  # -0.4% per °C
    )

    print(f"PV System: {system.panel_area} m² @ {system.panel_efficiency*100}% efficiency")
    print(f"Tilt: {system.tilt}°, Azimuth: {system.azimuth}° (South)")
    print()

    # Test different times throughout the day (summer solstice)
    date = datetime(2025, 6, 21, tzinfo=pytz.timezone("Europe/Prague"))
    times = [6, 9, 12, 15, 18]  # Hours of the day

    print("-" * 80)
    print("Solar Position and Irradiance Throughout the Day (June 21, 2025)")
    print("-" * 80)
    print(
        f"{'Time':>6} | {'Azimuth':>8} | {'Elevation':>9} | "
        f"{'GHI':>8} | {'DNI':>8} | {'DHI':>8}"
    )
    print(
        f"{'':>6} | {'(deg)':>8} | {'(deg)':>9} | "
        f"{'(W/m²)':>8} | {'(W/m²)':>8} | {'(W/m²)':>8}"
    )
    print("-" * 80)

    for hour in times:
        timestamp = date.replace(hour=hour, minute=0, second=0)

        # Calculate solar position
        position = calculate_solar_position(
            timestamp=timestamp,
            latitude=location.latitude,
            longitude=location.longitude,
            altitude=location.altitude,
        )

        # Calculate clear-sky irradiance (only if sun is above horizon)
        if position.elevation > 0:
            irradiance = calculate_clearsky_irradiance(
                apparent_elevation=position.elevation,
                latitude=location.latitude,
                longitude=location.longitude,
                altitude=location.altitude,
                model=ClearSkyModel.INEICHEN,
                linke_turbidity=3.0,
            )

            print(
                f"{hour:02d}:00 | {position.azimuth:8.2f} | {position.elevation:9.2f} | "
                f"{irradiance.ghi:8.1f} | {irradiance.dni:8.1f} | {irradiance.dhi:8.1f}"
            )
        else:
            print(
                f"{hour:02d}:00 | {position.azimuth:8.2f} | "
                f"{position.elevation:9.2f} | Sun below horizon"
            )

    print()

    # Compare clear-sky models at noon
    print("-" * 80)
    print("Comparison of Clear-Sky Models (Solar Noon)")
    print("-" * 80)

    noon = date.replace(hour=12, minute=0, second=0)
    noon_position = calculate_solar_position(
        timestamp=noon,
        latitude=location.latitude,
        longitude=location.longitude,
        altitude=location.altitude,
    )

    print(f"Solar Elevation: {noon_position.elevation:.2f}°")
    print()

    models = [
        ("Ineichen", ClearSkyModel.INEICHEN),
        ("Simplified Solis", ClearSkyModel.SIMPLIFIED_SOLIS),
    ]

    print(f"{'Model':>20} | {'GHI':>8} | {'DNI':>8} | {'DHI':>8}")
    print(f"{'':>20} | {'(W/m²)':>8} | {'(W/m²)':>8} | {'(W/m²)':>8}")
    print("-" * 80)

    for model_name, model in models:
        irr = calculate_clearsky_irradiance(
            apparent_elevation=noon_position.elevation,
            latitude=location.latitude,
            longitude=location.longitude,
            altitude=location.altitude,
            model=model,
            linke_turbidity=3.0,
        )
        print(f"{model_name:>20} | {irr.ghi:8.1f} | {irr.dni:8.1f} | {irr.dhi:8.1f}")

    print()

    # Compare different turbidity values
    print("-" * 80)
    print("Effect of Atmospheric Turbidity (Ineichen Model)")
    print("-" * 80)

    turbidities = [
        (2.0, "Very Clear"),
        (3.0, "Clear"),
        (4.0, "Moderate"),
        (5.0, "Turbid"),
    ]

    print(f"{'Turbidity':>12} | {'Description':>12} | {'GHI':>8} | {'DNI':>8} | {'DHI':>8}")
    print(f"{'':>12} | {'':>12} | {'(W/m²)':>8} | {'(W/m²)':>8} | {'(W/m²)':>8}")
    print("-" * 80)

    for turb, desc in turbidities:
        irr = calculate_clearsky_irradiance(
            apparent_elevation=noon_position.elevation,
            latitude=location.latitude,
            longitude=location.longitude,
            altitude=location.altitude,
            model=ClearSkyModel.INEICHEN,
            linke_turbidity=turb,
        )
        print(f"{turb:12.1f} | {desc:>12} | {irr.ghi:8.1f} | {irr.dni:8.1f} | {irr.dhi:8.1f}")

    print()
    print("=" * 80)
    print("Example Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
