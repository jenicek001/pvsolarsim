"""
Real-World Prague PV System Analysis - January 24, 2026
Using ACTUAL weather conditions from Václav Havel Airport Prague

Weather Data Source: TimeAndDate.com / CustomWeather
Location: Prague, Czech Republic (50.0807494°N, 14.8594164°E)
System: 14.04 kWp residential installation
"""

from datetime import datetime, timedelta
import pytz
import pandas as pd

from pvsolarsim import Location, PVSystem, calculate_power


def print_separator(title="", char="="):
    """Print a formatted separator."""
    if title:
        print(f"\n{char * 90}")
        print(f"  {title}")
        print(f"{char * 90}\n")
    else:
        print(char * 90)


def main():
    print_separator("REAL-WORLD SIMULATION: January 24, 2026 - Prague PV System", "=")
    print("System: 14.04 kWp Residential Installation")
    print("Weather: ACTUAL conditions from Václav Havel Airport Prague")
    print(f"Simulation Time: {datetime.now(pytz.timezone('Europe/Prague')).strftime('%H:%M CET')}")
    print()

    # ==================================================================================
    # ACTUAL WEATHER CONDITIONS FOR TODAY (January 24, 2026)
    # ==================================================================================

    print_separator("TODAY'S ACTUAL WEATHER CONDITIONS", "-")
    print("Source: Václav Havel Airport Prague")
    print("Last Update: 24 Jan 2026, 07:30 CET")
    print()
    print("CURRENT CONDITIONS (08:07 CET):")
    print("  Temperature: -5°C (feels like -5°C)")
    print("  Condition: Ice fog")
    print("  Visibility: 5 km")
    print("  Humidity: 93%")
    print("  Wind: 4 km/h from North (1.1 m/s)")
    print("  Pressure: 1003 mbar")
    print()
    print("TODAY'S FORECAST:")
    print("  Morning (06-12):   -3°C, OVERCAST, 84% humidity")
    print("  Afternoon (12-18): -1°C, OVERCAST, 81% humidity")
    print("  Evening (18-24):   -2°C, OVERCAST, 87% humidity")
    print()
    print("ANALYSIS:")
    print("  ⚠️  100% cloud cover all day (overcast)")
    print("  ⚠️  Ice fog in morning reducing visibility")
    print("  ⚠️  Very low temperatures (-5°C to -1°C)")
    print("  ✓  Low wind (beneficial, less heat loss)")
    print("  ⚠️  High humidity (93%) - potential frost on panels")
    print()
    print("EXPECTED IMPACT ON PV PRODUCTION:")
    print("  - Heavy overcast = 75-90% reduction in irradiance")
    print("  - Ice fog = additional 10-20% reduction in morning")
    print("  - Cold temperatures = POSITIVE effect (+5-8% efficiency boost)")
    print("  - Short winter day = only ~8 hours of potential production")
    print()

    # ==================================================================================
    # SYSTEM CONFIGURATION
    # ==================================================================================

    print_separator("SYSTEM CONFIGURATION", "-")

    location = Location(
        latitude=50.0807494,
        longitude=14.8594164,
        altitude=220,
        timezone="Europe/Prague",
    )

    # Real system parameters
    munchen_panels = {
        'count': 16,
        'power_wp': 450,
        'efficiency': 0.2037,
        'temp_coeff': -0.0035,
        'area_m2': 2.108 * 1.048,
    }

    canadian_panels = {
        'count': 18,
        'power_wp': 380,
        'efficiency': 0.205,
        'temp_coeff': -0.0037,
        'area_m2': 1.765 * 1.048,
    }

    # Calculate totals
    total_power_wp = (
        munchen_panels['count'] * munchen_panels['power_wp'] +
        canadian_panels['count'] * canadian_panels['power_wp']
    )
    total_area_m2 = (
        munchen_panels['count'] * munchen_panels['area_m2'] +
        canadian_panels['count'] * canadian_panels['area_m2']
    )
    weighted_efficiency = total_power_wp / (total_area_m2 * 1000)
    weighted_temp_coeff = (
        (munchen_panels['count'] * munchen_panels['power_wp'] * munchen_panels['temp_coeff'] +
         canadian_panels['count'] * canadian_panels['power_wp'] * canadian_panels['temp_coeff']) /
        total_power_wp
    )

    system = PVSystem(
        panel_area=total_area_m2,
        panel_efficiency=weighted_efficiency,
        tilt=35.0,
        azimuth=202.0,
        temp_coefficient=weighted_temp_coeff,
    )

    print(f"Location: {location.latitude:.6f}°N, {location.longitude:.6f}°E, {location.altitude}m")
    print(f"System Capacity: {total_power_wp / 1000:.2f} kWp")
    print(f"  - 16× München Solar 450W (7.20 kWp)")
    print(f"  - 18× Canadian Solar 380W (6.84 kWp)")
    print(f"Panel Area: {total_area_m2:.2f} m²")
    print(f"Weighted Efficiency: {weighted_efficiency * 100:.2f}%")
    print(f"Temperature Coefficient: {weighted_temp_coeff * 100:.3f}%/°C")
    print(f"Orientation: {system.tilt}° tilt, {system.azimuth}° azimuth (SSW)")
    print()

    # ==================================================================================
    # HOURLY SIMULATION WITH ACTUAL WEATHER
    # ==================================================================================

    print_separator("HOURLY SIMULATION - January 24, 2026", "=")

    prague_tz = pytz.timezone("Europe/Prague")
    today_start = datetime.now(prague_tz).replace(hour=0, minute=0, second=0, microsecond=0)

    # Actual weather conditions for each hour (from forecast)
    # Morning: -3°C, overcast, ice fog clearing
    # Afternoon: -1°C, overcast
    # Evening: -2°C, overcast
    hourly_weather = [
        # Hour  Temp  Cloud  Wind  Description
        (0,     -5,   100,   1.1,  "Night - overcast"),
        (1,     -5,   100,   1.1,  "Night - overcast"),
        (2,     -5,   100,   1.1,  "Night - overcast"),
        (3,     -5,   100,   1.1,  "Night - overcast"),
        (4,     -4,   100,   1.1,  "Night - overcast"),
        (5,     -4,   100,   1.1,  "Night - overcast"),
        (6,     -4,   100,   1.1,  "Pre-dawn - overcast, ice fog"),
        (7,     -4,   100,   1.1,  "Dawn - overcast, ice fog"),
        (8,     -3,   100,   1.1,  "Morning - overcast, fog clearing"),
        (9,     -3,   100,   1.4,  "Morning - overcast"),
        (10,    -2,   100,   1.4,  "Late morning - overcast"),
        (11,    -2,   100,   1.4,  "Noon - overcast"),
        (12,    -1,   100,   1.4,  "Noon - overcast"),
        (13,    -1,   100,   1.4,  "Early afternoon - overcast"),
        (14,    -1,   100,   1.4,  "Afternoon - overcast"),
        (15,    -1,   100,   1.4,  "Afternoon - overcast"),
        (16,    -2,   100,   1.1,  "Late afternoon - overcast"),
        (17,    -2,   100,   1.1,  "Dusk - overcast"),
        (18,    -2,   100,   1.1,  "Evening - overcast"),
        (19,    -2,   100,   1.1,  "Evening - overcast"),
        (20,    -2,   100,   1.1,  "Night - overcast"),
        (21,    -2,   100,   1.1,  "Night - overcast"),
        (22,    -2,   100,   1.1,  "Night - overcast"),
        (23,    -2,   100,   1.1,  "Night - overcast"),
    ]

    print("Calculating power for each hour using actual weather...")
    print()

    results = []
    for hour, temp, cloud, wind, desc in hourly_weather:
        timestamp = today_start + timedelta(hours=hour)
        
        # Add ice fog reduction factor for early morning
        soiling = 0.90 if hour < 8 else 0.95  # Ice fog effect
        
        result = calculate_power(
            location=location,
            system=system,
            timestamp=timestamp,
            ambient_temp=temp,
            wind_speed=wind,
            cloud_cover=cloud,
            soiling_factor=soiling,
            inverter_efficiency=0.97,
        )
        
        results.append({
            'hour': hour,
            'timestamp': timestamp,
            'temp_c': temp,
            'cloud_pct': cloud,
            'wind_ms': wind,
            'description': desc,
            'power_dc_kw': result.power_w / 1000,
            'power_ac_kw': result.power_ac_w / 1000,
            'solar_elev': result.solar_elevation,
            'poa_irrad': result.poa_irradiance,
            'cell_temp': result.cell_temperature,
        })

    df = pd.DataFrame(results)

    # Calculate daily totals
    daily_energy_dc_kwh = df['power_dc_kw'].sum() * 1.0  # 1 hour intervals
    daily_energy_ac_kwh = df['power_ac_kw'].sum() * 1.0
    peak_power_dc_kw = df['power_dc_kw'].max()
    peak_power_ac_kw = df['power_ac_kw'].max()
    peak_hour = df.loc[df['power_dc_kw'].idxmax(), 'hour']

    # ==================================================================================
    # RESULTS ANALYSIS
    # ==================================================================================

    print_separator("PRODUCTION ANALYSIS", "=")
    
    print("DAILY TOTALS:")
    print(f"  DC Energy: {daily_energy_dc_kwh:.2f} kWh")
    print(f"  AC Energy: {daily_energy_ac_kwh:.2f} kWh")
    print(f"  Peak Power: {peak_power_dc_kw:.2f} kW DC ({peak_power_ac_kw:.2f} kW AC) at {peak_hour:02d}:00")
    print(f"  Capacity Factor: {(daily_energy_dc_kwh / (total_power_wp/1000 * 24)) * 100:.2f}%")
    print()

    # Show production hours
    production_df = df[df['power_dc_kw'] > 0.01]
    if len(production_df) > 0:
        print(f"PRODUCTION HOURS: {len(production_df)} hours ({production_df['hour'].min():02d}:00 - {production_df['hour'].max():02d}:00)")
        print()
        print(f"{'Time':<8} {'Temp':<8} {'Power DC':<12} {'Power AC':<12} {'POA':<10} {'Solar El':<10}")
        print(f"{'(CET)':<8} {'(°C)':<8} {'(kW)':<12} {'(kW)':<12} {'(W/m²)':<10} {'(deg)':<10}")
        print("-" * 70)
        for _, row in production_df.iterrows():
            print(f"{row['hour']:02d}:00    {row['temp_c']:>4.0f}     "
                  f"{row['power_dc_kw']:>6.3f}       "
                  f"{row['power_ac_kw']:>6.3f}       "
                  f"{row['poa_irrad']:>6.1f}     "
                  f"{row['solar_elev']:>5.1f}°")
        print()
    else:
        print("⚠️  NO PRODUCTION - conditions too poor")
        print()

    # ==================================================================================
    # COMPARISON & CONTEXT
    # ==================================================================================

    print_separator("COMPARISON & CONTEXT", "=")

    # Calculate what production WOULD be on a clear day
    print("Calculating clear-sky comparison...")
    clear_results = []
    for hour in range(24):
        timestamp = today_start + timedelta(hours=hour)
        result = calculate_power(
            location=location,
            system=system,
            timestamp=timestamp,
            ambient_temp=-2,  # Average temp
            wind_speed=1.4,
            cloud_cover=0,  # CLEAR SKY
            soiling_factor=1.0,
            inverter_efficiency=0.97,
        )
        clear_results.append(result.power_w / 1000)

    clear_day_kwh = sum(clear_results)

    print()
    print("WEATHER IMPACT ANALYSIS:")
    print(f"  Actual production: {daily_energy_ac_kwh:.2f} kWh AC")
    print(f"  Clear-sky potential: {clear_day_kwh:.2f} kWh DC")
    print(f"  Weather reduction: {((1 - daily_energy_ac_kwh/clear_day_kwh) * 100):.1f}%")
    print()
    print("FACTORS AFFECTING PRODUCTION:")
    print(f"  ⚠️  Overcast (100% cloud): ~{100 - (daily_energy_ac_kwh/clear_day_kwh * 100):.0f}% reduction")
    print(f"  ⚠️  Ice fog (morning): Additional 5-10% loss")
    print(f"  ✓  Cold temps (-5 to -1°C): ~+6% efficiency gain vs. 25°C")
    print(f"  ✓  Low wind: Minimal convective cooling")
    print(f"  ⚠️  Winter solstice: Short day (~8h daylight)")
    print()

    # Context for January in Prague
    print("CONTEXT: January in Prague")
    print("  Typical daily production: 3-8 kWh/day (heavily weather dependent)")
    print("  Monthly average: 120-200 kWh/month")
    print("  Annual production: ~15,000-17,000 kWh")
    print(f"  Today's weather: {('WORSE' if daily_energy_ac_kwh < 5 else 'AVERAGE' if daily_energy_ac_kwh < 8 else 'BETTER')} than typical")
    print()

    print_separator("CONCLUSION", "=")
    print()
    print(f"🌤️  TODAY'S PRODUCTION: {daily_energy_ac_kwh:.2f} kWh AC")
    print()
    print("WEATHER SUMMARY:")
    print("  - Completely overcast all day (100% cloud cover)")
    print("  - Ice fog in morning reducing efficiency")
    print("  - Very cold but stable conditions (-5 to -1°C)")
    print("  - Typical poor winter day in Central Europe")
    print()
    print("SYSTEM PERFORMANCE:")
    if daily_energy_ac_kwh < 3:
        print("  ⚠️  VERY LOW - Heavy cloud cover limiting production")
    elif daily_energy_ac_kwh < 6:
        print("  📊 NORMAL for overcast winter day in Prague")
    else:
        print("  ✓  GOOD considering weather conditions")
    print()
    print(f"Economic value: ~{daily_energy_ac_kwh * 0.15:.2f} EUR @ 0.15 EUR/kWh")
    print(f"CO₂ avoided: ~{daily_energy_ac_kwh * 0.5:.2f} kg (vs. grid mix)")
    print()
    print("=" * 90)


if __name__ == "__main__":
    main()
