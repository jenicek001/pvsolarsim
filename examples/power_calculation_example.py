"""Example: Calculate PV power output.

This example demonstrates how to calculate instantaneous power output from a
PV system using the pvsolarsim library.
"""

from datetime import datetime

import pytz

from pvsolarsim import Location, PVSystem, calculate_power

# Define location (e.g., Jihlava, Czech Republic)
location = Location(
    latitude=49.8,  # degrees North
    longitude=15.5,  # degrees East
    altitude=300,  # meters above sea level
    timezone="Europe/Prague",
)

# Define PV system
system = PVSystem(
    panel_area=20.0,  # 20 m² of panels
    panel_efficiency=0.20,  # 20% efficiency (typical for crystalline silicon)
    tilt=35.0,  # 35° tilt (optimal for this latitude)
    azimuth=180.0,  # South-facing (180° in northern hemisphere)
    temp_coefficient=-0.004,  # -0.4%/°C (typical for c-Si)
)

print("=" * 70)
print("PV Power Calculation Example")
print("=" * 70)

# Example 1: Calculate power at solar noon on summer solstice
print("\n1. Summer Solstice (June 21) at Noon")
print("-" * 70)
timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)
result = calculate_power(
    location=location,
    system=system,
    timestamp=timestamp,
    ambient_temp=25,  # °C
    wind_speed=3,  # m/s
)

print(f"Time: {timestamp}")
print(f"Solar Elevation: {result.solar_elevation:.2f}°")
print(f"Solar Azimuth: {result.solar_azimuth:.2f}°")
print(f"GHI: {result.ghi:.2f} W/m²")
print(f"DNI: {result.dni:.2f} W/m²")
print(f"DHI: {result.dhi:.2f} W/m²")
print(f"POA Global Irradiance: {result.poa_irradiance:.2f} W/m²")
print(f"POA Direct: {result.poa_direct:.2f} W/m²")
print(f"POA Diffuse: {result.poa_diffuse:.2f} W/m²")
print(f"Cell Temperature: {result.cell_temperature:.2f}°C")
print(f"Temperature Factor: {result.temperature_factor:.4f}")
print(f"DC Power Output: {result.power_w:.2f} W ({result.power_w/1000:.2f} kW)")

# Example 2: Compare different cloud cover conditions
print("\n2. Cloud Cover Comparison (Same time)")
print("-" * 70)
for cloud_cover in [0, 25, 50, 75, 100]:
    result = calculate_power(
        location, system, timestamp, ambient_temp=25, wind_speed=3, cloud_cover=cloud_cover
    )
    print(
        f"Cloud Cover {cloud_cover:3d}%: {result.power_w:7.2f} W "
        f"(POA: {result.poa_irradiance:6.2f} W/m²)"
    )

# Example 3: Compare winter vs summer
print("\n3. Seasonal Comparison")
print("-" * 70)
summer = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)
winter = datetime(2025, 12, 21, 12, 0, tzinfo=pytz.UTC)

result_summer = calculate_power(location, system, summer, ambient_temp=25)
result_winter = calculate_power(location, system, winter, ambient_temp=0)

print("Summer Solstice:")
print(f"  Elevation: {result_summer.solar_elevation:.2f}°")
print(f"  Power: {result_summer.power_w:.2f} W")

print("Winter Solstice:")
print(f"  Elevation: {result_winter.solar_elevation:.2f}°")
print(f"  Power: {result_winter.power_w:.2f} W")

print(f"Ratio: {result_summer.power_w / result_winter.power_w:.2f}x")

# Example 4: Temperature effect
print("\n4. Temperature Effect (Same irradiance)")
print("-" * 70)
for temp in [-10, 0, 10, 20, 30, 40, 50]:
    result = calculate_power(location, system, timestamp, ambient_temp=temp, wind_speed=3)
    print(
        f"Ambient {temp:3d}°C → Cell {result.cell_temperature:5.2f}°C → "
        f"Temp Factor {result.temperature_factor:.4f} → "
        f"Power {result.power_w:7.2f} W"
    )

# Example 5: Degradation and soiling
print("\n5. Degradation and Soiling Effects")
print("-" * 70)
result_new = calculate_power(
    location,
    system,
    timestamp,
    soiling_factor=1.0,  # Clean panels
    degradation_factor=1.0,  # New panels
)

result_aged = calculate_power(
    location,
    system,
    timestamp,
    soiling_factor=0.95,  # 5% soiling loss
    degradation_factor=0.90,  # 10% degradation (10 years old)
)

print(f"New, clean panels: {result_new.power_w:.2f} W")
print(f"Aged, dirty panels: {result_aged.power_w:.2f} W")
print(f"Total loss: {(1 - result_aged.power_w/result_new.power_w)*100:.1f}%")

# Example 6: With inverter
print("\n6. DC vs AC Power (with inverter)")
print("-" * 70)
result_with_inverter = calculate_power(
    location, system, timestamp, inverter_efficiency=0.96
)

print(f"DC Power: {result_with_inverter.power_w:.2f} W")
print(f"AC Power: {result_with_inverter.power_ac_w:.2f} W")
print("Inverter Efficiency: 96%")

# Example 7: Daily power curve
print("\n7. Daily Power Curve (Hourly)")
print("-" * 70)
print("Time (UTC)  |  Elevation  |  POA (W/m²)  |  Power (W)")
print("-" * 70)
for hour in [6, 8, 10, 12, 14, 16, 18, 20]:
    timestamp = datetime(2025, 6, 21, hour, 0, tzinfo=pytz.UTC)
    result = calculate_power(location, system, timestamp)
    print(
        f"  {hour:02d}:00     | {result.solar_elevation:7.2f}°  | "
        f"{result.poa_irradiance:10.2f}  | {result.power_w:9.2f}"
    )

print("\n" + "=" * 70)
print("Example complete!")
print("=" * 70)
