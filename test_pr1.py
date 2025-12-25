"""
Test PR #1 - Solar position and clear-sky irradiance calculations
for specific location: 50.0807494N, 14.8594164E
with roof tilt 35° and azimuth 202°
"""

from datetime import datetime
import pytz

from pvsolarsim.solar import calculate_solar_position
from pvsolarsim.atmosphere import calculate_clearsky_irradiance, ClearSkyModel

def main():
    print("=" * 80)
    print("Testing PR #1: Solar Position and Clear-Sky Irradiance")
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
        'efficiency': 0.2037,  # 20.37%
        'temp_coeff_pmax': -0.0035,  # -0.35%/°C
        'temp_coeff_voc': -0.00304,  # -0.304%/°C
        'temp_coeff_isc': 0.0005,  # 0.05%/°C
        'area_m2': 2.108 * 1.048,  # 2.209 m²
        'noct': 42,  # °C (±2°C)
        'cell_type': 'Monocrystalline half-cut',
        'cells': 144
    }
    
    # 18x Canadian Solar HiKu CS3L-380MS
    canadian_panels = {
        'count': 18,
        'power_wp': 380,
        'efficiency': 0.205,  # ~20.5% (estimated from power/area)
        'temp_coeff_pmax': -0.0037,  # -0.37%/°C (typical for PERC)
        'temp_coeff_voc': -0.0028,  # -0.28%/°C (typical)
        'temp_coeff_isc': 0.0005,  # 0.05%/°C (typical)
        'area_m2': 1.765 * 1.048,  # 1.850 m²
        'noct': 42,  # °C (±3°C, typical for HiKu series)
        'vmp': 34.5,  # V
        'imp': 11.02,  # A
        'voc': 41.2,  # V
        'isc': 11.68,  # A
        'cell_type': 'Monocrystalline PERC',
        'cells': 120
    }
    
    # Total system
    total_power_wp = (munchen_panels['count'] * munchen_panels['power_wp'] + 
                      canadian_panels['count'] * canadian_panels['power_wp'])
    total_area_m2 = (munchen_panels['count'] * munchen_panels['area_m2'] + 
                     canadian_panels['count'] * canadian_panels['area_m2'])
    weighted_efficiency = total_power_wp / (total_area_m2 * 1000)  # At STC (1000 W/m²)
    weighted_temp_coeff = ((munchen_panels['count'] * munchen_panels['power_wp'] * munchen_panels['temp_coeff_pmax'] +
                           canadian_panels['count'] * canadian_panels['power_wp'] * canadian_panels['temp_coeff_pmax']) /
                          total_power_wp)
    
    print(f"Location: {latitude}°N, {longitude}°E")
    print(f"Altitude: {altitude}m")
    print()
    print(f"PV System Configuration:")
    print(f"  Orientation: Tilt {tilt}°, Azimuth {azimuth}° (SSW)")
    print(f"  Panel Type 1: {munchen_panels['count']}x München MSMD450M6-72 @ {munchen_panels['power_wp']}W")
    print(f"    - Total: {munchen_panels['count'] * munchen_panels['power_wp']/1000:.1f} kWp")
    print(f"    - Efficiency: {munchen_panels['efficiency']*100:.2f}%")
    print(f"    - Temp coeff: {munchen_panels['temp_coeff_pmax']*100:.2f}%/°C")
    print(f"  Panel Type 2: {canadian_panels['count']}x Canadian Solar CS3L-380MS @ {canadian_panels['power_wp']}W")
    print(f"    - Total: {canadian_panels['count'] * canadian_panels['power_wp']/1000:.1f} kWp")
    print(f"    - Efficiency: {canadian_panels['efficiency']*100:.2f}%")
    print(f"    - Temp coeff: {canadian_panels['temp_coeff_pmax']*100:.2f}%/°C")
    print()
    print(f"  System Total: {total_power_wp/1000:.2f} kWp")
    print(f"  Total Area: {total_area_m2:.2f} m²")
    print(f"  Weighted Efficiency: {weighted_efficiency*100:.2f}%")
    print(f"  Weighted Temp Coefficient: {weighted_temp_coeff*100:.3f}%/°C")
    print()
    
    # Test for today (December 25, 2025) at specified hours
    timezone = pytz.timezone("Europe/Prague")
    date = datetime(2025, 12, 25, tzinfo=timezone)
    hours = [9, 10, 11, 12, 13, 14, 15, 16]
    
    print("-" * 80)
    print(f"Solar Position and Irradiance - December 25, 2025 (Prague timezone)")
    print("-" * 80)
    print(f"{'Time':>6} | {'Azimuth':>8} | {'Elevation':>9} | "
          f"{'GHI':>8} | {'DNI':>8} | {'DHI':>8}")
    print(f"{'':>6} | {'(deg)':>8} | {'(deg)':>9} | "
          f"{'(W/m²)':>8} | {'(W/m²)':>8} | {'(W/m²)':>8}")
    print("-" * 80)
    
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
    print("-" * 80)
    print("Detailed Analysis at Solar Noon")
    print("-" * 80)
    
    # Find solar noon (around 12:00 local time in winter)
    noon = date.replace(hour=12, minute=0, second=0)
    noon_position = calculate_solar_position(
        timestamp=noon,
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
    )
    
    print(f"\nSolar Position at {noon.strftime('%H:%M %Z')}:")
    print(f"  Azimuth: {noon_position.azimuth:.2f}° (180° = South)")
    print(f"  Elevation: {noon_position.elevation:.2f}°")
    print(f"  Zenith: {noon_position.zenith:.2f}°")
    
    # Test both clear-sky models
    print(f"\nClear-Sky Irradiance Models Comparison:")
    
    models = [
        ("Ineichen", ClearSkyModel.INEICHEN),
        ("Simplified Solis", ClearSkyModel.SIMPLIFIED_SOLIS),
    ]
    
    for model_name, model in models:
        irr = calculate_clearsky_irradiance(
            apparent_elevation=noon_position.elevation,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            model=model,
            linke_turbidity=3.0,
        )
        print(f"\n  {model_name}:")
        print(f"    GHI: {irr.ghi:8.1f} W/m²")
        print(f"    DNI: {irr.dni:8.1f} W/m²")
        print(f"    DHI: {irr.dhi:8.1f} W/m²")
    
    # Analyze roof orientation
    print(f"\n" + "-" * 80)
    print("Roof Orientation Analysis")
    print("-" * 80)
    print(f"\nYour roof: Tilt = {tilt}°, Azimuth = {azimuth}° (SSW)")
    print(f"Sun at noon: Azimuth = {noon_position.azimuth:.2f}°")
    print(f"\nAzimuth difference from due south (180°): {abs(azimuth - 180):.1f}°")
    print(f"Your roof is oriented {azimuth - 180:.1f}° west of south")
    print(f"\nNote: This is a good orientation for afternoon energy capture!")
    print(f"December has low sun angle ({noon_position.elevation:.1f}° at noon),")
    print(f"so your 35° tilt is well-suited for winter production.")
    
    # Theoretical power estimation (simplified)
    print(f"\n" + "-" * 80)
    print("Estimated Instantaneous Power at Solar Noon (Clear Sky)")
    print("-" * 80)
    
    # Note: This is a rough estimate - actual POA calculation comes in Week 4
    # For now, just show potential with GHI and simple cosine factor
    irr_noon = calculate_clearsky_irradiance(
        apparent_elevation=noon_position.elevation,
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        model=ClearSkyModel.INEICHEN,
        linke_turbidity=3.0,
    )
    
    # Very rough estimate: assume GHI ≈ POA for winter with 35° tilt
    # (actual POA calculation with diffuse components comes in Week 4)
    estimated_poa = irr_noon.ghi * 0.9  # Rough adjustment
    
    # Temperature derating (assume panel temp 10°C above ambient at 0°C)
    assumed_ambient_temp = 0  # °C (winter in Prague)
    assumed_panel_temp = assumed_ambient_temp + 10
    temp_derating = 1 + weighted_temp_coeff * (assumed_panel_temp - 25)
    
    estimated_power_w = total_power_wp * (estimated_poa / 1000) * temp_derating
    
    print(f"\nSimplified calculation (for reference only):")
    print(f"  GHI at noon: {irr_noon.ghi:.1f} W/m²")
    print(f"  Estimated POA: {estimated_poa:.1f} W/m² (rough)")
    print(f"  System capacity: {total_power_wp/1000:.2f} kWp")
    print(f"  Assumed ambient temp: {assumed_ambient_temp}°C")
    print(f"  Estimated panel temp: {assumed_panel_temp}°C")
    print(f"  Temperature derating: {temp_derating:.3f}")
    print(f"  **Estimated power: {estimated_power_w/1000:.2f} kW**")
    print(f"\nNote: This is a very rough estimate!")
    print(f"Actual power calculation requires:")
    print(f"  - POA irradiance (Week 4 - accounts for tilt, orientation, diffuse)")
    print(f"  - Accurate temperature model (Week 5 - NOCT-based)")
    print(f"  - IAM corrections (Week 4 - angle of incidence losses)")
    
    print()
    print("=" * 80)
    print("Test Complete!")
    print("=" * 80)
    print("\nNext steps in the library development:")
    print("- Week 4: Plane-of-array (POA) irradiance calculation")
    print("  (will calculate actual irradiance on your tilted/oriented roof)")
    print("- Week 5: Temperature modeling (using NOCT)")
    print("- Week 6: Instantaneous power calculation")
    print("- Week 7: Annual energy simulation")
    print(f"\nYour system ({total_power_wp/1000:.2f} kWp) will benefit from accurate modeling!")


if __name__ == "__main__":
    main()
