#!/usr/bin/env python3
"""
Temperature Modeling Example
=============================

This example demonstrates PV cell/module temperature modeling using different
models and calculating the effect on power output.

Temperature significantly affects PV performance - typically reducing power by
0.3-0.5% per degree Celsius above 25°C (STC conditions).
"""

import numpy as np
from datetime import datetime
import pytz

from pvsolarsim import (
    calculate_cell_temperature,
    calculate_temperature_correction_factor,
)
from pvsolarsim.temperature import faiman_model, sapm_model, pvsyst_model


def example_basic_temperature():
    """Basic temperature calculation example."""
    print("=" * 70)
    print("Example 1: Basic Cell Temperature Calculation")
    print("=" * 70)

    # Typical sunny day conditions
    poa_irradiance = 800  # W/m²
    ambient_temp = 25  # °C
    wind_speed = 3  # m/s

    # Calculate using Faiman model (default)
    cell_temp = calculate_cell_temperature(
        poa_global=poa_irradiance,
        temp_air=ambient_temp,
        wind_speed=wind_speed
    )

    print(f"Irradiance: {poa_irradiance} W/m²")
    print(f"Ambient temperature: {ambient_temp}°C")
    print(f"Wind speed: {wind_speed} m/s")
    print(f"\nCell temperature: {cell_temp:.2f}°C")
    print(f"Temperature rise: {cell_temp - ambient_temp:.2f}°C")
    print()


def example_compare_models():
    """Compare different temperature models."""
    print("=" * 70)
    print("Example 2: Comparing Temperature Models")
    print("=" * 70)

    poa = 1000  # W/m²
    t_air = 20  # °C
    wind = 2  # m/s

    print(f"Conditions: {poa} W/m², {t_air}°C ambient, {wind} m/s wind")
    print()

    # Faiman model
    temp_faiman = faiman_model(poa, t_air, wind)
    print(f"Faiman model:         {temp_faiman:.2f}°C")

    # SAPM model
    temp_sapm = sapm_model(poa, t_air, wind)
    print(f"SAPM model:           {temp_sapm:.2f}°C")

    # PVsyst model (with typical c-Si parameters)
    temp_pvsyst = pvsyst_model(
        poa, t_air, wind,
        module_efficiency=0.20,
        alpha_absorption=0.88
    )
    print(f"PVsyst model:         {temp_pvsyst:.2f}°C")
    print(f"\nTemperature range:    {temp_pvsyst:.2f}°C - {temp_sapm:.2f}°C")
    print(f"Model variation:      {temp_sapm - temp_pvsyst:.2f}°C")
    print()


def example_power_impact():
    """Demonstrate temperature effect on power output."""
    print("=" * 70)
    print("Example 3: Temperature Impact on Power Output")
    print("=" * 70)

    # 300W monocrystalline module
    rated_power = 300  # W (at STC: 1000 W/m², 25°C)
    temp_coefficient = -0.004  # -0.4%/°C (typical for c-Si)

    # Scenario: Hot summer day
    poa = 1000  # Full sun
    t_air = 35  # Hot day
    wind = 1  # Low wind

    cell_temp = calculate_cell_temperature(poa, t_air, wind)

    # Calculate temperature correction
    temp_correction = calculate_temperature_correction_factor(
        cell_temperature=cell_temp,
        temp_coefficient=temp_coefficient
    )

    # Actual power (considering only temperature loss)
    actual_power = rated_power * temp_correction

    print(f"Module: {rated_power}W at STC (1000 W/m², 25°C)")
    print(f"Temperature coefficient: {temp_coefficient*100:.1f}%/°C")
    print()
    print(f"Conditions:")
    print(f"  Irradiance:         {poa} W/m²")
    print(f"  Ambient temp:       {t_air}°C")
    print(f"  Wind speed:         {wind} m/s")
    print()
    print(f"Results:")
    print(f"  Cell temperature:   {cell_temp:.1f}°C")
    print(f"  Temp. rise:         {cell_temp - 25:.1f}°C above STC")
    print(f"  Correction factor:  {temp_correction:.4f}")
    print(f"  Power output:       {actual_power:.1f}W")
    print(f"  Power loss:         {rated_power - actual_power:.1f}W ({(1-temp_correction)*100:.1f}%)")
    print()


def example_daily_variation():
    """Show temperature variation over a day."""
    print("=" * 70)
    print("Example 4: Daily Temperature Variation")
    print("=" * 70)

    # Simulate a sunny day
    hours = np.array([6, 8, 10, 12, 14, 16, 18])
    irradiance = np.array([100, 400, 700, 1000, 900, 500, 100])  # W/m²
    ambient_temps = np.array([15, 18, 22, 28, 30, 28, 22])  # °C
    wind_speeds = np.array([1, 1.5, 2, 2.5, 3, 2, 1])  # m/s

    print("Time  | Irrad. | T_amb | Wind | T_cell | Power Loss")
    print("------|--------|-------|------|--------|------------")

    for i in range(len(hours)):
        cell_temp = calculate_cell_temperature(
            poa_global=irradiance[i],
            temp_air=ambient_temps[i],
            wind_speed=wind_speeds[i]
        )

        correction = calculate_temperature_correction_factor(
            cell_temperature=cell_temp,
            temp_coefficient=-0.004
        )

        print(f"{hours[i]:2d}:00 | {irradiance[i]:4.0f} W | "
              f"{ambient_temps[i]:4.1f}° | {wind_speeds[i]:3.1f}  | "
              f"{cell_temp:5.1f}° | {(1-correction)*100:5.1f}%")

    print()


def example_wind_effect():
    """Demonstrate wind cooling effect."""
    print("=" * 70)
    print("Example 5: Wind Cooling Effect")
    print("=" * 70)

    poa = 1000
    t_air = 30

    print(f"Conditions: {poa} W/m², {t_air}°C ambient")
    print()
    print("Wind Speed | Cell Temp | Cooling Effect")
    print("-----------|-----------|----------------")

    wind_speeds = [0, 1, 2, 3, 4, 5]
    temps = []

    for wind in wind_speeds:
        cell_temp = calculate_cell_temperature(poa, t_air, wind)
        temps.append(cell_temp)

        if wind == 0:
            print(f"{wind:5.0f} m/s  | {cell_temp:7.2f}°C | (baseline)")
        else:
            cooling = temps[0] - cell_temp
            print(f"{wind:5.0f} m/s  | {cell_temp:7.2f}°C | -{cooling:5.2f}°C")

    print()
    print(f"Total cooling effect: {temps[0] - temps[-1]:.2f}°C (0 to 5 m/s)")
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("PVSolarSim - Temperature Modeling Examples")
    print("=" * 70)
    print()

    example_basic_temperature()
    example_compare_models()
    example_power_impact()
    example_daily_variation()
    example_wind_effect()

    print("=" * 70)
    print("Examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
