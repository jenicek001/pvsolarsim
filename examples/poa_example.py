"""
Example demonstrating plane-of-array (POA) irradiance calculations.

This example shows how to calculate POA irradiance on tilted solar panels
using different diffuse transposition models and incidence angle modifiers.
"""

from datetime import datetime

import pytz

from pvsolarsim.atmosphere import calculate_clearsky_irradiance
from pvsolarsim.irradiance import POAIrradiance, calculate_poa_irradiance
from pvsolarsim.solar import calculate_solar_position


def main():
    """Demonstrate POA irradiance calculations."""
    print("=" * 70)
    print("POA Irradiance Calculation Example")
    print("=" * 70)

    # Define location (Prague, Czech Republic)
    latitude = 50.0755
    longitude = 14.4378
    altitude = 200.0

    # Define PV system parameters
    panel_tilt = 35.0  # degrees from horizontal
    panel_azimuth = 180.0  # South-facing

    # Define time (summer midday in local time)
    timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.timezone("Europe/Prague"))

    print(f"\nLocation: Prague ({latitude}°N, {longitude}°E)")
    print(f"Date/Time: {timestamp} (local time)")
    print(f"Panel: {panel_tilt}° tilt, {panel_azimuth}° azimuth (South)")

    # Step 1: Calculate solar position
    print("\n" + "-" * 70)
    print("STEP 1: Calculate Solar Position")
    print("-" * 70)
    solar_pos = calculate_solar_position(timestamp, latitude, longitude, altitude)
    print(f"Solar Azimuth: {solar_pos.azimuth:.2f}°")
    print(f"Solar Elevation: {solar_pos.elevation:.2f}°")
    print(f"Solar Zenith: {solar_pos.zenith:.2f}°")

    # Step 2: Calculate clear-sky irradiance
    print("\n" + "-" * 70)
    print("STEP 2: Calculate Clear-Sky Irradiance")
    print("-" * 70)
    irradiance = calculate_clearsky_irradiance(
        apparent_elevation=solar_pos.elevation,
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        model="ineichen",
        linke_turbidity=3.0,  # Typical clear sky
    )
    print(f"GHI (Global Horizontal): {irradiance.ghi:.2f} W/m²")
    print(f"DNI (Direct Normal):     {irradiance.dni:.2f} W/m²")
    print(f"DHI (Diffuse Horizontal): {irradiance.dhi:.2f} W/m²")

    # Step 3: Calculate POA irradiance with different models
    print("\n" + "-" * 70)
    print("STEP 3: Calculate POA Irradiance (Different Models)")
    print("-" * 70)

    diffuse_models = ["isotropic", "perez", "haydavies"]
    for model in diffuse_models:
        poa = calculate_poa_irradiance(
            surface_tilt=panel_tilt,
            surface_azimuth=panel_azimuth,
            solar_zenith=solar_pos.zenith,
            solar_azimuth=solar_pos.azimuth,
            dni=irradiance.dni,
            ghi=irradiance.ghi,
            dhi=irradiance.dhi,
            diffuse_model=model,
            albedo=0.2,  # Typical ground
        )

        print(f"\n{model.upper()} Model:")
        print(f"  POA Direct:   {poa.poa_direct:.2f} W/m²")
        print(f"  POA Diffuse:  {poa.poa_diffuse:.2f} W/m²")
        print(f"  POA Ground:   {poa.poa_ground:.2f} W/m²")
        print(f"  POA Global:   {poa.poa_global:.2f} W/m²")

    # Step 4: Compare different albedo values
    print("\n" + "-" * 70)
    print("STEP 4: Effect of Ground Albedo")
    print("-" * 70)

    albedos = {
        "Asphalt": 0.1,
        "Grass": 0.2,
        "Concrete": 0.3,
        "Sand": 0.4,
        "Snow": 0.8,
    }

    for surface, albedo in albedos.items():
        poa = calculate_poa_irradiance(
            surface_tilt=panel_tilt,
            surface_azimuth=panel_azimuth,
            solar_zenith=solar_pos.zenith,
            solar_azimuth=solar_pos.azimuth,
            dni=irradiance.dni,
            ghi=irradiance.ghi,
            dhi=irradiance.dhi,
            diffuse_model="perez",
            albedo=albedo,
        )
        print(
            f"{surface:10s} (albedo={albedo:.1f}): "
            f"Ground={poa.poa_ground:5.1f} W/m², Total={poa.poa_global:6.1f} W/m²"
        )

    # Step 5: Compare IAM models
    print("\n" + "-" * 70)
    print("STEP 5: Effect of Incidence Angle Modifiers (IAM)")
    print("-" * 70)

    iam_models = ["ashrae", "physical", "martin_ruiz"]
    for iam in iam_models:
        poa_calc = POAIrradiance(diffuse_model="perez", iam_model=iam, albedo=0.2)
        poa = poa_calc.calculate(
            surface_tilt=panel_tilt,
            surface_azimuth=panel_azimuth,
            solar_zenith=solar_pos.zenith,
            solar_azimuth=solar_pos.azimuth,
            dni=irradiance.dni,
            ghi=irradiance.ghi,
            dhi=irradiance.dhi,
        )
        print(
            f"{iam.upper():15s}: Direct={poa.poa_direct:6.1f} W/m², "
            f"Total={poa.poa_global:6.1f} W/m²"
        )

    # Step 6: Daily profile (simplified)
    print("\n" + "-" * 70)
    print("STEP 6: POA Irradiance Throughout the Day")
    print("-" * 70)

    poa_calc = POAIrradiance(diffuse_model="perez", albedo=0.2)

    print(f"\n{'Time':>6s} {'Elev':>6s} {'GHI':>8s} {'POA Global':>10s}")
    print("-" * 35)

    for hour in [6, 8, 10, 12, 14, 16, 18]:
        ts = datetime(2025, 6, 21, hour, 0, tzinfo=pytz.timezone("Europe/Prague"))
        sol_pos = calculate_solar_position(ts, latitude, longitude, altitude)

        if sol_pos.elevation > 0:
            irr = calculate_clearsky_irradiance(
                apparent_elevation=sol_pos.elevation,
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                model="ineichen",
                linke_turbidity=3.0,
            )

            poa = poa_calc.calculate(
                surface_tilt=panel_tilt,
                surface_azimuth=panel_azimuth,
                solar_zenith=sol_pos.zenith,
                solar_azimuth=sol_pos.azimuth,
                dni=irr.dni,
                ghi=irr.ghi,
                dhi=irr.dhi,
            )

            print(
                f"{hour:02d}:00  {sol_pos.elevation:5.1f}°  "
                f"{irr.ghi:7.1f}  {poa.poa_global:9.1f} W/m²"
            )
        else:
            print(f"{hour:02d}:00  (sun below horizon)")

    print("\n" + "=" * 70)
    print("Key Findings:")
    print("- Perez model gives more accurate diffuse irradiance than isotropic")
    print("- High albedo (snow) significantly increases ground-reflected component")
    print("- IAM reduces direct irradiance at high angles of incidence")
    print("- POA global can exceed GHI for optimally tilted south-facing panels")
    print("=" * 70)


if __name__ == "__main__":
    main()
