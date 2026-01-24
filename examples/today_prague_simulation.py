"""
Real-World Prague PV System - Today's Performance
Date: January 17, 2026

This script calculates actual power output for the real Prague installation
for today's conditions.
"""

from datetime import datetime, timedelta

import pytz

from pvsolarsim import Location, PVSystem, calculate_power


def main():
    print("=" * 90)
    print("REAL-WORLD PV SYSTEM: Today's Performance Analysis")
    print("14.04 kWp System in Prague, Czech Republic")
    print(f"Date: {datetime.now().strftime('%B %d, %Y')}")
    print("=" * 90)
    print()

    # ==================================================================================
    # SYSTEM CONFIGURATION
    # ==================================================================================

    # Location
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

    print("System Configuration:")
    print(f"  Location: Prague ({location.latitude}°N, {location.longitude}°E, {location.altitude}m)")
    print(f"  Total Capacity: {total_power_wp / 1000:.2f} kWp")
    print(f"  Panel Area: {total_area_m2:.2f} m²")
    print(f"  Efficiency: {weighted_efficiency * 100:.2f}%")
    print(f"  Orientation: {system.tilt}° tilt, {system.azimuth}° azimuth (SSW)")
    print()

    # ==================================================================================
    # TODAY'S WEATHER CONDITIONS
    # ==================================================================================

    print("⚠️  IMPORTANT: SIMULATED WEATHER DATA")
    print("=" * 90)
    print("This simulation uses CLEAR-SKY MODEL, not real weather data!")
    print()
    print("Why? Real weather APIs require:")
    print("  • API key (OpenWeatherMap, Visual Crossing, etc.)")
    print("  • Historical data access (often paid)")
    print("  • Real-time weather stations nearby")
    print()
    print("For REALISTIC results, you need to:")
    print("  1. Get API key from weather service")
    print("  2. Use weather_source='openweathermap' or 'csv' with real data")
    print("  3. Or manually enter today's actual conditions below")
    print()
    print("=" * 90)
    print()

    # CLEAR-SKY simulation parameters (optimistic)
    # For realistic January in Prague, multiply results by 0.15-0.30
    ambient_temp = 0.0  # °C (typical winter)
    wind_speed = 3.5  # m/s (moderate winter wind)
    cloud_cover = 0  # % (CLEAR SKY - unrealistic for Prague winter!)

    print("Simulation Settings (CLEAR-SKY MODEL):")
    print(f"  Temperature: {ambient_temp}°C")
    print(f"  Wind Speed: {wind_speed} m/s")
    print(f"  Cloud Cover: {cloud_cover}% (CLEAR SKY - unrealistic!)")
    print()
    print("Typical January Prague Weather (from ČHMÚ):")
    print("  • Average cloud cover: 75-85%")
    print("  • Average sunshine: 1-2 hours/day")
    print("  • Expected daily energy: 5-15 kWh (NOT 40-50 kWh!)")
    print()

    # ==================================================================================
    # HOURLY SIMULATION FOR TODAY
    # ==================================================================================

    print("Hourly Power Output for Today:")
    print("-" * 90)
    print("Time (Prague)    Solar Elev  POA (W/m²)  Cell Temp  DC Power    AC Power    Daily Total")
    print("-" * 90)

    # Prague timezone
    prague_tz = pytz.timezone('Europe/Prague')
    today = datetime.now(prague_tz).replace(hour=0, minute=0, second=0, microsecond=0)

    total_energy_wh = 0.0
    hourly_results = []

    # Simulate every hour from sunrise to sunset
    for hour in range(24):
        timestamp = today + timedelta(hours=hour)
        
        result = calculate_power(
            location=location,
            system=system,
            timestamp=timestamp,
            ambient_temp=ambient_temp,
            wind_speed=wind_speed,
            cloud_cover=cloud_cover,
            soiling_factor=0.95,  # 5% soiling loss (winter, more dirt/snow)
            inverter_efficiency=0.96,
        )

        # Calculate energy for this hour (Wh)
        energy_wh = result.power_w if result.power_w > 0 else 0
        total_energy_wh += energy_wh

        # Only show hours with some production (or key hours)
        if result.power_w > 10 or hour in [6, 7, 8, 12, 16, 17, 18]:
            solar_elev = 90 - result.solar_zenith if hasattr(result, 'solar_zenith') else 0
            
            print(f"{timestamp.strftime('%H:%M %Z'):16s} "
                  f"{solar_elev:10.1f}° "
                  f"{result.poa_irradiance:10.1f} "
                  f"{result.cell_temperature:10.1f}°C "
                  f"{result.power_w:10.1f} W "
                  f"{result.power_ac_w if result.power_ac_w else 0:10.1f} W "
                  f"{total_energy_wh / 1000:10.2f} kWh")
            
            hourly_results.append({
                'time': timestamp,
                'power_w': result.power_w,
                'power_ac_w': result.power_ac_w or 0,
                'energy_wh': energy_wh,
            })

    print("-" * 90)
    print()

    # ==================================================================================
    # DAILY SUMMARY
    # ==================================================================================

    print("Daily Summary (January 17, 2026 - CLEAR-SKY MODEL):")
    print("-" * 90)
    print(f"  Total Energy (DC): {total_energy_wh / 1000:.2f} kWh")
    
    total_energy_ac_wh = sum(r['power_ac_w'] for r in hourly_results)
    print(f"  Total Energy (AC): {total_energy_ac_wh / 1000:.2f} kWh")
    print()
    print("  ⚠️  WARNING: This is CLEAR-SKY (perfect weather) simulation!")
    print(f"  Realistic January expectation: {(total_energy_ac_wh / 1000) * 0.20:.2f} kWh/day")
    print("  (Prague winter typically has 75-85% cloud cover)")
    print()
    if hourly_results:
        max_power = max(r['power_ac_w'] for r in hourly_results)
        print(f"  Peak Power: {max_power / 1000:.2f} kW")
        
        # Production hours (power > 10W)
        production_hours = sum(1 for r in hourly_results if r['power_ac_w'] > 10)
        print(f"  Production Hours: {production_hours} hours")
    
    # Daily performance ratio
    system_capacity_kwh = total_power_wp / 1000
    capacity_utilization = (total_energy_ac_wh / 1000) / (system_capacity_kwh * 24) * 100
    print(f"  Daily Capacity Factor: {capacity_utilization:.2f}%")
    print()

    # ==================================================================================
    # COMPARISON WITH EXPECTED PERFORMANCE
    # ==================================================================================

    print("Comparison with Real-World Performance:")
    print("-" * 90)
    
    # Realistic January in Prague (from PVGIS and real installations)
    # January: ~30-40 kWh/m²/month GHI → ~1.0-1.3 kWh/m²/day average
    # With clouds: 0.2-0.4 kWh/m²/day typical
    realistic_daily_ghi = 0.3  # kWh/m²/day (typical cloudy January)
    realistic_daily_energy = realistic_daily_ghi * total_area_m2 * weighted_efficiency * 0.75
    
    clear_sky_daily_ghi = 1.5  # kWh/m²/day (perfect clear sky)
    clear_sky_daily_energy = total_energy_ac_wh / 1000
    
    print(f"  CLEAR-SKY (this simulation): {clear_sky_daily_energy:.2f} kWh/day")
    print(f"  REALISTIC January typical: {realistic_daily_energy:.2f} kWh/day")
    print(f"  Reduction factor: {(realistic_daily_energy / clear_sky_daily_energy) * 100:.1f}%")
    print()
    print("  Real Prague January conditions:")
    print("    • 75-85% cloud cover most days")
    print("    • 1-2 hours direct sun on average")
    print("    • Monthly total: 150-250 kWh (not 1,500 kWh!)")
    print("    • Daily range: 3-20 kWh depending on weather")
    print()

    # ==================================================================================
    # ECONOMIC VALUE
    # ==================================================================================

    print("Economic Value:")
    print("-" * 90)
    
    # Czech electricity prices
    electricity_price_czk = 6.50  # CZK/kWh
    feed_in_tariff_czk = 2.50  # CZK/kWh
    self_consumption_ratio = 0.40
    
    # Use realistic values
    realistic_daily_energy_kwh = realistic_daily_energy
    
    self_consumed_kwh = realistic_daily_energy_kwh * self_consumption_ratio
    exported_kwh = realistic_daily_energy_kwh * (1 - self_consumption_ratio)
    
    daily_value_czk = (
        self_consumed_kwh * electricity_price_czk +
        exported_kwh * feed_in_tariff_czk
    )
    
    print("  REALISTIC January typical day:")
    print(f"    Self-consumed: {self_consumed_kwh:.2f} kWh × {electricity_price_czk} CZK = {self_consumed_kwh * electricity_price_czk:.2f} CZK")
    print(f"    Exported: {exported_kwh:.2f} kWh × {feed_in_tariff_czk} CZK = {exported_kwh * feed_in_tariff_czk:.2f} CZK")
    print(f"    Daily Value: {daily_value_czk:.2f} CZK (~{daily_value_czk / 24:.2f} EUR)")
    print()
    
    # Monthly and annual projection
    monthly_value_czk = daily_value_czk * 31  # January has 31 days
    
    print(f"  Projected January (31 days): {monthly_value_czk:.2f} CZK (~{monthly_value_czk / 24:.2f} EUR)")
    print()
    print("  Annual realistic estimate (with weather variation):")
    print("    • January-February: ~150 kWh/month each (~25 EUR/month)")
    print("    • March-April: ~800 kWh/month each (~135 EUR/month)")
    print("    • May-July: ~1,400 kWh/month each (~235 EUR/month)")
    print("    • August-October: ~900 kWh/month each (~150 EUR/month)")
    print("    • November-December: ~200 kWh/month each (~35 EUR/month)")
    print("    • Total: ~15,000 kWh/year (~2,500 EUR/year)")
    print()

    # ==================================================================================
    # RECOMMENDATIONS
    # ==================================================================================

    print("How to Get REAL Weather Data:")
    print("-" * 90)
    print()
    print("This simulation used CLEAR-SKY model (perfect weather). For real results:")
    print()
    print("Option 1: Use Weather API")
    print("  • Get free API key from OpenWeatherMap or Visual Crossing")
    print("  • Modify this script to use weather_source='openweathermap'")
    print("  • Example:")
    print("    results = simulate_annual(..., weather_source='openweathermap',")
    print("                               api_key='YOUR_KEY')")
    print()
    print("Option 2: Use CSV with Real Data")
    print("  • Download data from weather station or PVGIS")
    print("  • Save as CSV with columns: timestamp, ghi, dni, dhi, temp_air, wind_speed")
    print("  • Use weather_source='csv', file_path='weather.csv'")
    print()
    print("Option 3: Manual Measurement")
    print("  • Check your inverter's production today")
    print("  • Compare with this simulation's clear-sky value")
    print(f"  • Clear-sky max: {clear_sky_daily_energy:.1f} kWh")
    print(f"  • Realistic typical: {realistic_daily_energy:.1f} kWh")
    print("  • Your actual today: ??? kWh (check inverter)")
    print()
    print("Winter Operation Tips:")
    print("  • January typically produces 1.5-2% of annual energy")
    print("  • Check panels for snow accumulation")
    print("  • Cold temps improve efficiency when sun does shine")
    print("  • Don't expect more than 10-20 kWh/day in January!")
    print()

    print("=" * 90)
    print("Simulation complete!")
    print("=" * 90)


if __name__ == "__main__":
    main()
