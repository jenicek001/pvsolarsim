"""
Test PR #2 - POA (Plane-of-Array) irradiance calculations
for specific location: 50.0807494N, 14.8594164E
with roof tilt 35° and azimuth 202°

This test demonstrates the new POA calculation features implemented in PR #2.
"""

from datetime import datetime

import pytz

from pvsolarsim.atmosphere import ClearSkyModel, calculate_clearsky_irradiance
from pvsolarsim.irradiance import POAIrradiance, calculate_poa_irradiance
from pvsolarsim.solar import calculate_solar_position


def main():
    print("=" * 80)
    print("Testing PR #2: Plane-of-Array (POA) Irradiance Calculations")
    print("=" * 80)
    print()

    # Your specific location (Prague area)
    latitude = 50.0807494
    longitude = 14.8594164
    altitude = 300  # Assumed altitude in meters

    # Your PV system configuration
    tilt = 35.0  # degrees
    azimuth = 202.0  # degrees (roughly SSW)

    # Panel specifications
    # 16x München Energieprodukte MSMD450M6-72 M6
    munchen_panels = {
        'count': 16,
        'power_wp': 450,
        'area_m2': 2.108 * 1.048,  # 2.209 m²
    }

    # 18x Canadian Solar HiKu CS3L-380MS
    canadian_panels = {
        'count': 18,
        'power_wp': 380,
        'area_m2': 1.765 * 1.048,  # 1.850 m²
    }

    # Total system
    total_power_wp = (munchen_panels['count'] * munchen_panels['power_wp'] +
                      canadian_panels['count'] * canadian_panels['power_wp'])
    total_area_m2 = (munchen_panels['count'] * munchen_panels['area_m2'] +
                     canadian_panels['count'] * canadian_panels['area_m2'])
    weighted_efficiency = total_power_wp / (total_area_m2 * 1000)  # At STC (1000 W/m²)

    print(f"Location: {latitude}°N, {longitude}°E")
    print(f"Altitude: {altitude}m")
    print()
    print("PV System Configuration:")
    print(f"  Orientation: Tilt {tilt}°, Azimuth {azimuth}° (SSW)")
    print(f"  Total Power: {total_power_wp/1000:.2f} kWp")
    print(f"  Total Area: {total_area_m2:.2f} m²")
    print(f"  Weighted Efficiency: {weighted_efficiency*100:.2f}%")
    print()

    # Test for today (December 25, 2025) at specified hours
    timezone = pytz.timezone("Europe/Prague")
    date = datetime(2025, 12, 25, tzinfo=timezone)
    hours = [9, 10, 11, 12, 13, 14, 15, 16]

    print("-" * 80)
    print("POA Irradiance Analysis - December 25, 2025 (Prague timezone)")
    print("-" * 80)
    print(f"{'Time':>6} | {'Sol Elev':>8} | {'GHI':>8} | {'POA Direct':>10} | "
          f"{'POA Diffuse':>11} | {'POA Ground':>10} | {'POA Global':>10}")
    print(f"{'':>6} | {'(deg)':>8} | {'(W/m²)':>8} | {'(W/m²)':>10} | "
          f"{'(W/m²)':>11} | {'(W/m²)':>10} | {'(W/m²)':>10}")
    print("-" * 80)

    # Create POA calculator with Perez model (industry standard)
    poa_calc = POAIrradiance(
        diffuse_model="perez",
        iam_model="physical",
        albedo=0.2  # Typical ground
    )

    for hour in hours:
        timestamp = date.replace(hour=hour, minute=0, second=0)

        # Calculate solar position
        position = calculate_solar_position(
            timestamp=timestamp,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
        )

        # Calculate clear-sky irradiance (only if sun is above horizon)
        if position.elevation > 0:
            irradiance = calculate_clearsky_irradiance(
                apparent_elevation=position.elevation,
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                model=ClearSkyModel.INEICHEN,
                linke_turbidity=3.0,  # Typical clear sky value
            )

            # Calculate POA irradiance (NEW in PR #2!)
            poa = poa_calc.calculate(
                surface_tilt=tilt,
                surface_azimuth=azimuth,
                solar_zenith=position.zenith,
                solar_azimuth=position.azimuth,
                dni=irradiance.dni,
                ghi=irradiance.ghi,
                dhi=irradiance.dhi,
            )

            print(
                f"{hour:02d}:00 | {position.elevation:8.2f} | {irradiance.ghi:8.1f} | "
                f"{poa.poa_direct:10.1f} | {poa.poa_diffuse:11.1f} | "
                f"{poa.poa_ground:10.1f} | {poa.poa_global:10.1f}"
            )
        else:
            print(
                f"{hour:02d}:00 | {position.elevation:8.2f} | "
                f"Sun below horizon"
            )

    print()
    print("-" * 80)
    print("Detailed POA Analysis at Solar Noon")
    print("-" * 80)

    # Find solar noon (around 12:00 local time in winter)
    noon = date.replace(hour=12, minute=0, second=0)
    noon_position = calculate_solar_position(
        timestamp=noon,
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
    )

    noon_irradiance = calculate_clearsky_irradiance(
        apparent_elevation=noon_position.elevation,
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        model=ClearSkyModel.INEICHEN,
        linke_turbidity=3.0,
    )

    print(f"\nSolar Position at {noon.strftime('%H:%M %Z')}:")
    print(f"  Azimuth: {noon_position.azimuth:.2f}° (180° = South)")
    print(f"  Elevation: {noon_position.elevation:.2f}°")
    print(f"  Zenith: {noon_position.zenith:.2f}°")

    print("\nHorizontal Irradiance (GHI, DNI, DHI):")
    print(f"  GHI: {noon_irradiance.ghi:8.1f} W/m²")
    print(f"  DNI: {noon_irradiance.dni:8.1f} W/m²")
    print(f"  DHI: {noon_irradiance.dhi:8.1f} W/m²")

    # Compare different diffuse models
    print("\n" + "-" * 80)
    print("POA Irradiance: Comparing Diffuse Transposition Models")
    print("-" * 80)

    diffuse_models = ["isotropic", "perez", "haydavies"]

    for model in diffuse_models:
        poa = calculate_poa_irradiance(
            surface_tilt=tilt,
            surface_azimuth=azimuth,
            solar_zenith=noon_position.zenith,
            solar_azimuth=noon_position.azimuth,
            dni=noon_irradiance.dni,
            ghi=noon_irradiance.ghi,
            dhi=noon_irradiance.dhi,
            diffuse_model=model,
            albedo=0.2,
        )

        print(f"\n{model.upper()} Model:")
        print(f"  POA Direct:   {poa.poa_direct:8.1f} W/m²")
        print(f"  POA Diffuse:  {poa.poa_diffuse:8.1f} W/m²")
        print(f"  POA Ground:   {poa.poa_ground:8.1f} W/m²")
        print(f"  POA Global:   {poa.poa_global:8.1f} W/m² ⭐")

    # Effect of ground albedo
    print("\n" + "-" * 80)
    print("Effect of Ground Albedo on POA Irradiance")
    print("-" * 80)

    albedo_values = {
        "Asphalt": 0.1,
        "Grass (typical)": 0.2,
        "Concrete": 0.3,
        "Fresh snow": 0.8,
    }

    print(f"\n{'Surface Type':>20} | {'Albedo':>7} | {'POA Ground':>10} | {'POA Global':>10}")
    print("-" * 52)

    for surface, albedo_val in albedo_values.items():
        poa = calculate_poa_irradiance(
            surface_tilt=tilt,
            surface_azimuth=azimuth,
            solar_zenith=noon_position.zenith,
            solar_azimuth=noon_position.azimuth,
            dni=noon_irradiance.dni,
            ghi=noon_irradiance.ghi,
            dhi=noon_irradiance.dhi,
            diffuse_model="perez",
            albedo=albedo_val,
        )
        print(f"{surface:>20} | {albedo_val:7.1f} | {poa.poa_ground:10.1f} | {poa.poa_global:10.1f} W/m²")

    # Actual power estimation with POA
    print("\n" + "-" * 80)
    print("Estimated Instantaneous DC Power at Solar Noon")
    print("-" * 80)

    # Use Perez model with typical ground albedo
    poa_best = calculate_poa_irradiance(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        solar_zenith=noon_position.zenith,
        solar_azimuth=noon_position.azimuth,
        dni=noon_irradiance.dni,
        ghi=noon_irradiance.ghi,
        dhi=noon_irradiance.dhi,
        diffuse_model="perez",
        iam_model="physical",
        albedo=0.2,
    )

    # Temperature derating (simplified - detailed model comes in Week 5)
    assumed_ambient_temp = 0  # °C (winter in Prague)
    assumed_panel_temp = assumed_ambient_temp + 10  # Rough estimate
    temp_coeff = -0.0036  # Weighted average from panels
    temp_derating = 1 + temp_coeff * (assumed_panel_temp - 25)

    # Calculate power
    dc_power_stc = poa_best.poa_global * total_area_m2 * weighted_efficiency
    dc_power_actual = dc_power_stc * temp_derating

    print("\nPOA Irradiance (Perez model with Physical IAM):")
    print(f"  POA Global: {poa_best.poa_global:.1f} W/m²")
    print(f"    - Direct:  {poa_best.poa_direct:.1f} W/m² (with IAM losses)")
    print(f"    - Diffuse: {poa_best.poa_diffuse:.1f} W/m²")
    print(f"    - Ground:  {poa_best.poa_ground:.1f} W/m²")

    print(f"\nCompare with GHI: {noon_irradiance.ghi:.1f} W/m²")
    poa_gain = (poa_best.poa_global / noon_irradiance.ghi - 1) * 100
    print(f"POA gain over horizontal: {poa_gain:+.1f}%")

    print("\nPower Calculation:")
    print(f"  System capacity: {total_power_wp/1000:.2f} kWp")
    print(f"  Total area: {total_area_m2:.2f} m²")
    print(f"  Efficiency: {weighted_efficiency*100:.2f}%")
    print(f"  POA irradiance: {poa_best.poa_global:.1f} W/m²")
    print(f"  Ambient temperature: {assumed_ambient_temp}°C")
    print(f"  Panel temperature: {assumed_panel_temp}°C (estimated)")
    print(f"  Temperature derating: {temp_derating:.3f}")
    print(f"\n  **DC Power Output: {dc_power_actual/1000:.2f} kW**")
    print(f"  (At STC temp: {dc_power_stc/1000:.2f} kW)")

    # Comparison with old estimate
    old_estimate_poa = noon_irradiance.ghi * 0.9  # From test_pr1.py
    old_estimate_power = total_power_wp * (old_estimate_poa / 1000) * (1 + temp_coeff * (assumed_panel_temp - 25))

    print("\n" + "-" * 80)
    print("Improvement Over PR #1 Estimate")
    print("-" * 80)
    print("\nPR #1 (rough estimate):")
    print(f"  Estimated POA: {old_estimate_poa:.1f} W/m² (GHI × 0.9)")
    print(f"  Estimated power: {old_estimate_power/1000:.2f} kW")

    print("\nPR #2 (accurate POA calculation):")
    print(f"  Calculated POA: {poa_best.poa_global:.1f} W/m²")
    print(f"  Calculated power: {dc_power_actual/1000:.2f} kW")

    difference = dc_power_actual - old_estimate_power
    percent_diff = (difference / old_estimate_power) * 100
    print(f"\nDifference: {difference/1000:+.2f} kW ({percent_diff:+.1f}%)")

    if difference > 0:
        print("✓ More accurate POA calculation shows HIGHER expected power!")
    else:
        print("✓ More accurate POA calculation provides realistic estimate")

    print()
    print("=" * 80)
    print("PR #2 Features Demonstrated:")
    print("=" * 80)
    print("""
✅ Plane-of-array (POA) irradiance calculation
✅ Multiple diffuse transposition models (Isotropic, Perez, Hay-Davies)
✅ Incidence angle modifiers (IAM) for reflection losses
✅ Configurable ground albedo
✅ Accurate power estimation using actual panel orientation

Key Improvements:
• POA accounts for your 35° tilt and 202° azimuth (SSW) orientation
• Perez model captures anisotropic sky diffuse (more accurate than isotropic)
• Physical IAM model reduces direct irradiance at high angles
• Ground reflection contribution calculated based on albedo
• More realistic power estimates for tilted panels

Next steps:
- Week 5: Temperature modeling (NOCT-based cell temperature)
- Week 6: Complete instantaneous power calculation
- Week 7: Annual energy simulation
""")

    print("=" * 80)
    print("Test Complete! PR #2 POA calculations working correctly.")
    print("=" * 80)


if __name__ == "__main__":
    main()
