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
    # TODAY'S WEATHER CONDITIONS (Typical January in Prague)
    # ==================================================================================

    # January weather estimates for Prague
    # Source: Czech Hydrometeorological Institute average data
    ambient_temp = 0.0  # °C (typical winter)
    wind_speed = 3.5  # m/s (moderate winter wind)
    cloud_cover = 80  # % (Prague is typically cloudy in January)

    print("Weather Conditions (Typical January in Prague):")
    print(f"  Temperature: {ambient_temp}°C (winter average)")
    print(f"  Wind Speed: {wind_speed} m/s")
    print(f"  Cloud Cover: {cloud_cover}% (typical winter cloudiness)")
    print(f"  Note: Using estimated weather - for actual conditions integrate weather API")
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

    print("Daily Summary (January 17, 2026):")
    print("-" * 90)
    print(f"  Total Energy (DC): {total_energy_wh / 1000:.2f} kWh")
    
    total_energy_ac_wh = sum(r['power_ac_w'] for r in hourly_results)
    print(f"  Total Energy (AC): {total_energy_ac_wh / 1000:.2f} kWh")
    
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

    print("Comparison with Expected Performance:")
    print("-" * 90)
    
    # January average for Prague (from PVGIS)
    # Average GHI for January in Prague: ~30 kWh/m²/month → ~1 kWh/m²/day
    expected_daily_ghi = 1.0  # kWh/m²/day
    expected_daily_energy = expected_daily_ghi * total_area_m2 * weighted_efficiency * 0.75  # 75% PR
    
    print(f"  Expected January Daily Energy: {expected_daily_energy:.2f} kWh (clear day average)")
    print(f"  Today's Actual Energy: {total_energy_ac_wh / 1000:.2f} kWh")
    
    if expected_daily_energy > 0:
        performance_vs_expected = (total_energy_ac_wh / 1000) / expected_daily_energy * 100
        print(f"  Performance vs Expected: {performance_vs_expected:.1f}%")
        
        if performance_vs_expected > 90:
            print("  Status: ✓ Excellent - above average performance")
        elif performance_vs_expected > 70:
            print("  Status: ✓ Good - near expected performance")
        elif performance_vs_expected > 50:
            print("  Status: ⚠ Fair - below average (cloudy day)")
        else:
            print("  Status: ⚠ Poor - significant cloudiness or issues")
    print()

    # ==================================================================================
    # ECONOMIC VALUE
    # ==================================================================================

    print("Economic Value (Today):")
    print("-" * 90)
    
    # Czech electricity prices
    electricity_price_czk = 6.50  # CZK/kWh
    feed_in_tariff_czk = 2.50  # CZK/kWh
    self_consumption_ratio = 0.40
    
    self_consumed_kwh = (total_energy_ac_wh / 1000) * self_consumption_ratio
    exported_kwh = (total_energy_ac_wh / 1000) * (1 - self_consumption_ratio)
    
    daily_value_czk = (
        self_consumed_kwh * electricity_price_czk +
        exported_kwh * feed_in_tariff_czk
    )
    
    print(f"  Self-consumed: {self_consumed_kwh:.2f} kWh × {electricity_price_czk} CZK = {self_consumed_kwh * electricity_price_czk:.2f} CZK")
    print(f"  Exported: {exported_kwh:.2f} kWh × {feed_in_tariff_czk} CZK = {exported_kwh * feed_in_tariff_czk:.2f} CZK")
    print(f"  Total Daily Value: {daily_value_czk:.2f} CZK (~{daily_value_czk / 24:.2f} EUR)")
    print()
    
    # Monthly and annual projection
    monthly_value_czk = daily_value_czk * 31  # January has 31 days
    annual_projection_czk = daily_value_czk * 365
    
    print(f"  Projected January Value: {monthly_value_czk:.2f} CZK (~{monthly_value_czk / 24:.2f} EUR)")
    print(f"  If every day like today: {annual_projection_czk:.2f} CZK/year (~{annual_projection_czk / 24:.2f} EUR/year)")
    print("  Note: January is the lowest production month; annual average is ~6× higher")
    print()

    # ==================================================================================
    # RECOMMENDATIONS
    # ==================================================================================

    print("Today's Recommendations:")
    print("-" * 90)
    
    if cloud_cover > 70:
        print("  • High cloud cover reducing output by ~50-70%")
        print("  • This is normal for January in Prague")
        print("  • Spring/summer will show much better performance")
    
    if ambient_temp < 5:
        print("  • Cold temperatures actually improve panel efficiency!")
        print("  • Panels perform better in winter (when there's sun)")
    
    print("  • Check for snow accumulation on panels")
    print("  • Winter months typically produce 15-20% of annual energy")
    print("  • Peak production months (May-July) will be 6-8× higher")
    print()

    print("=" * 90)
    print("Simulation complete!")
    print("=" * 90)


if __name__ == "__main__":
    main()
