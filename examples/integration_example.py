"""
Comprehensive integration example demonstrating all implemented features.

This example shows how to use PVSolarSim to calculate solar position,
clear-sky irradiance, and POA irradiance for a complete PV system analysis.
"""

from datetime import datetime

import pytz

from pvsolarsim import Location, PVSystem
from pvsolarsim.atmosphere import calculate_clearsky_irradiance
from pvsolarsim.irradiance import calculate_poa_irradiance
from pvsolarsim.solar import calculate_solar_position


def main():
    """Demonstrate complete PV system analysis workflow."""
    print("=" * 80)
    print("PVSolarSim - Complete Integration Example")
    print("=" * 80)

    # Step 1: Define Location
    print("\n" + "=" * 80)
    print("STEP 1: Define Location")
    print("=" * 80)

    location = Location(
        latitude=40.7589,  # Denver, CO
        longitude=-105.0150,
        altitude=1655.0,  # meters
        timezone="America/Denver",
    )

    print("Location: Denver, Colorado")
    print(f"  Latitude:  {location.latitude}°")
    print(f"  Longitude: {location.longitude}°")
    print(f"  Altitude:  {location.altitude} m")
    print(f"  Timezone:  {location.timezone}")

    # Step 2: Define PV System
    print("\n" + "=" * 80)
    print("STEP 2: Define PV System")
    print("=" * 80)

    system = PVSystem(
        panel_area=20.0,  # m² (e.g., 10 panels × 2m²)
        panel_efficiency=0.20,  # 20% (modern silicon)
        tilt=40.0,  # degrees (optimized for latitude)
        azimuth=180.0,  # South-facing
        temp_coefficient=-0.004,  # -0.4%/°C (typical for silicon)
    )

    print("PV System Configuration:")
    print(f"  Panel Area:        {system.panel_area} m²")
    print(f"  Panel Efficiency:  {system.panel_efficiency * 100}%")
    print(f"  Tilt Angle:        {system.tilt}° from horizontal")
    print(f"  Azimuth:           {system.azimuth}° (South)")
    print(f"  Temp Coefficient:  {system.temp_coefficient * 100}%/°C")

    # Step 3: Analyze Summer Solstice
    print("\n" + "=" * 80)
    print("STEP 3: Summer Solstice Analysis (June 21, 2025)")
    print("=" * 80)

    # Create timezone-aware timestamp
    timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.timezone("America/Denver"))
    print(f"\nTime: {timestamp}")

    # Calculate solar position
    solar_pos = calculate_solar_position(
        timestamp=timestamp,
        latitude=location.latitude,
        longitude=location.longitude,
        altitude=location.altitude,
    )

    print("\nSolar Position:")
    print(f"  Azimuth:    {solar_pos.azimuth:.2f}° (0° = North, 180° = South)")
    print(f"  Elevation:  {solar_pos.elevation:.2f}° (angle above horizon)")
    print(f"  Zenith:     {solar_pos.zenith:.2f}° (angle from vertical)")

    # Calculate clear-sky irradiance
    irradiance = calculate_clearsky_irradiance(
        apparent_elevation=solar_pos.elevation,
        latitude=location.latitude,
        longitude=location.longitude,
        altitude=location.altitude,
        model="ineichen",
        linke_turbidity=3.0,  # Clear sky
    )

    print("\nClear-Sky Irradiance:")
    print(f"  GHI (Global Horizontal): {irradiance.ghi:.2f} W/m²")
    print(f"  DNI (Direct Normal):     {irradiance.dni:.2f} W/m²")
    print(f"  DHI (Diffuse Horizontal): {irradiance.dhi:.2f} W/m²")

    # Calculate POA irradiance
    poa = calculate_poa_irradiance(
        surface_tilt=system.tilt,
        surface_azimuth=system.azimuth,
        solar_zenith=solar_pos.zenith,
        solar_azimuth=solar_pos.azimuth,
        dni=irradiance.dni,
        ghi=irradiance.ghi,
        dhi=irradiance.dhi,
        diffuse_model="perez",
        albedo=0.2,
    )

    print("\nPlane-of-Array (POA) Irradiance:")
    print(f"  Direct Component:   {poa.poa_direct:.2f} W/m²")
    print(f"  Diffuse Component:  {poa.poa_diffuse:.2f} W/m²")
    print(f"  Ground Reflected:   {poa.poa_ground:.2f} W/m²")
    print(f"  Total POA Global:   {poa.poa_global:.2f} W/m²")

    # Calculate instantaneous DC power (simplified, without temperature effects)
    dc_power = poa.poa_global * system.panel_area * system.panel_efficiency
    print("\nEstimated DC Power Output (at STC temperature):")
    print(f"  {dc_power:.2f} W ({dc_power / 1000:.2f} kW)")

    # Step 4: Daily Profile
    print("\n" + "=" * 80)
    print("STEP 4: Daily Irradiance Profile (Summer Solstice)")
    print("=" * 80)

    print(
        f"\n{'Time':>8s} {'Solar Elev':>11s} {'GHI':>8s} "
        f"{'POA Global':>11s} {'DC Power':>10s}"
    )
    print("-" * 60)

    daily_energy_wh = 0  # Watt-hours

    for hour in range(5, 21):  # 5 AM to 8 PM
        ts = datetime(2025, 6, 21, hour, 0, tzinfo=pytz.timezone("America/Denver"))
        sol_pos = calculate_solar_position(
            ts, location.latitude, location.longitude, location.altitude
        )

        if sol_pos.elevation > 0:
            irr = calculate_clearsky_irradiance(
                sol_pos.elevation,
                location.latitude,
                location.longitude,
                location.altitude,
                model="ineichen",
                linke_turbidity=3.0,
            )

            poa_irr = calculate_poa_irradiance(
                system.tilt,
                system.azimuth,
                sol_pos.zenith,
                sol_pos.azimuth,
                irr.dni,
                irr.ghi,
                irr.dhi,
                diffuse_model="perez",
                albedo=0.2,
            )

            power = poa_irr.poa_global * system.panel_area * system.panel_efficiency
            daily_energy_wh += power  # Simple hour-based integration

            print(
                f"{hour:02d}:00    {sol_pos.elevation:5.1f}°      "
                f"{irr.ghi:7.1f}  {poa_irr.poa_global:10.1f}  {power:9.1f} W"
            )
        else:
            print(f"{hour:02d}:00    (sun below horizon)")

    daily_energy_kwh = daily_energy_wh / 1000
    print(f"\nEstimated Daily Energy Production: {daily_energy_kwh:.2f} kWh")
    print(
        "(Note: This is a simplified calculation. Actual production depends on "
        "temperature, soiling, inverter efficiency, etc.)"
    )

    # Step 5: Comparison with Different Orientations
    print("\n" + "=" * 80)
    print("STEP 5: Orientation Comparison (12:00 PM)")
    print("=" * 80)

    configurations = [
        ("Horizontal (0° tilt)", 0, 180),
        ("Optimal (40° tilt, South)", 40, 180),
        ("Steep (60° tilt, South)", 60, 180),
        ("Vertical (90° tilt, South)", 90, 180),
        ("East-facing (40° tilt)", 40, 90),
        ("West-facing (40° tilt)", 40, 270),
    ]

    print(f"\n{'Configuration':>30s} {'POA Global':>12s} {'DC Power':>10s}")
    print("-" * 55)

    for name, tilt, azimuth in configurations:
        poa_config = calculate_poa_irradiance(
            tilt,
            azimuth,
            solar_pos.zenith,
            solar_pos.azimuth,
            irradiance.dni,
            irradiance.ghi,
            irradiance.dhi,
            diffuse_model="perez",
            albedo=0.2,
        )

        power_config = poa_config.poa_global * system.panel_area * system.panel_efficiency
        print(
            f"{name:>30s} {poa_config.poa_global:11.1f} W/m²  "
            f"{power_config:9.1f} W"
        )

    # Summary
    print("\n" + "=" * 80)
    print("Summary & Key Takeaways")
    print("=" * 80)
    print(
        """
1. POA Global can exceed GHI for properly oriented panels
   - South-facing panels capture more irradiance than horizontal at solar noon
   - Tilt angle optimization is location and season dependent

2. Different diffuse models affect results:
   - Perez model (used here) accounts for horizon brightening
   - More accurate than simple isotropic model

3. Ground reflection contributes to total irradiance:
   - Albedo of 0.2 (grass) adds modest contribution
   - High albedo (snow: 0.8) significantly increases POA

4. Orientation significantly impacts energy production:
   - Optimal tilt ≈ latitude for year-round production
   - East/West facing reduces midday production but spreads output

5. Temperature effects (not yet implemented):
   - Panel temperature typically 20-30°C above ambient
   - Reduces efficiency by 8-12% on hot days
   - Coming in Week 5 implementation!
"""
    )

    print("=" * 80)
    print("Example Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
