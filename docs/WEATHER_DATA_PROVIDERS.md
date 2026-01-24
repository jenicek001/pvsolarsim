# Weather Data Providers for PV Solar Simulation

**Last Updated:** January 17, 2026  
**Status:** Research Complete

---

## Executive Summary

This document compares weather data providers for real-world PV simulation. **Key finding:** For PVSolarSim users, **Visual Crossing** and **PVGIS** offer the best value, while **Windy.com does NOT provide solar irradiance data**.

### Quick Recommendations

| Use Case | Recommended Provider | Cost | Why |
|----------|---------------------|------|-----|
| **Development/Testing** | PVGIS TMY | FREE | Free European TMY data, no API key needed |
| **Small Projects** | Visual Crossing | FREE (1000 req/day) | Best free tier, includes solar radiation |
| **Production Use** | Visual Crossing | $49/month | Unlimited calls, solar radiation included |
| **Enterprise** | Solcast | Custom pricing | Highest accuracy, PV-specific features |

---

## 1. PVGIS (Photovoltaic Geographical Information System)

**Provider:** European Commission Joint Research Centre  
**Website:** https://re.jrc.ec.europa.eu/pvgis.html

### ✅ Advantages
- **FREE** (no API key required)
- **Coverage:** Europe, Africa, Asia (most of the world)
- **Data Quality:** High-quality satellite + ground station fusion
- **TMY Data:** Typical Meteorological Year (2005-2020)
- **Solar Specific:** Designed specifically for PV applications
- **Open Access:** No registration needed for basic use

### Data Provided
- Global Horizontal Irradiance (GHI)
- Direct Normal Irradiance (DNI)
- Diffuse Horizontal Irradiance (DHI)
- Air Temperature
- Wind Speed
- Relative Humidity

### Limitations
- **No real-time data** (only TMY and historical)
- **No weather forecasts**
- **API rate limits** for automated queries
- **Time period:** 2005-2020 (not recent years)

### Pricing
**FREE** (EU-funded public service)

### Best For
- **Development and testing**
- **Academic research**
- **European installations**
- **Long-term average simulations**

### PVSolarSim Integration Status
✅ **Already implemented** in `pvsolarsim.weather.api_clients.PVGISClient`

---

## 2. Visual Crossing Weather API

**Provider:** Visual Crossing Corporation  
**Website:** https://www.visualcrossing.com/

### ✅ Advantages
- **Generous free tier:** 1,000 records/day
- **Very affordable:** $0.0001 per record (pay-as-you-go)
- **Solar radiation data** included (GHI, DNI, DHI, GTI)
- **Historical data:** Back to 1950s
- **Forecasts:** 15-day weather forecast
- **Global coverage**
- **Easy API:** Simple REST interface, JSON/CSV output

### Data Provided
- Global Horizontal Irradiance (GHI)
- Direct Normal Irradiance (DNI)
- Diffuse Horizontal Irradiance (DHI)
- Global Tilted Irradiance (GTI) - **unique feature**
- Solar azimuth and elevation
- Temperature, humidity, wind, precipitation
- Cloud cover

### Pricing Plans
| Plan | Price | Calls | Best For |
|------|-------|-------|----------|
| **Free** | $0 | 1,000 records/day | Development, small projects |
| **Pay-as-you-go** | $0.0001/record | Unlimited | Variable usage |
| **Monthly** | $49/month | Unlimited | Production apps |
| **Annual** | $499/year | Unlimited | 15% savings |

**Example costs:**
- 1 year hourly data (8,760 records) = $0.88
- 10 years hourly data (87,600 records) = $8.76
- Real-time annual monitoring (365 days × 24 calls) = $0.88

### Limitations
- Free tier limited to 1,000 records/day
- Solar radiation only in premium plans (check current tier)
- Some advanced features require paid plans

### Best For
- **Production applications**
- **Real-world validation**
- **Multi-year historical analysis**
- **Commercial projects**

### PVSolarSim Integration Status
⏭️ **Not yet implemented** (planned for future release)

---

## 3. OpenWeatherMap

**Provider:** OpenWeather Ltd.  
**Website:** https://openweathermap.org/

### ⚠️ **EXPENSIVE for Solar Data**
- Standard weather API: Free tier available
- **Solar Irradiance API:** Separate subscription
- **Cost:** ~$800/month for solar radiation access

### Data Provided (Solar Subscription)
- Global Horizontal Irradiance (GHI)
- Direct Normal Irradiance (DNI)
- Diffuse Horizontal Irradiance (DHI)
- Historical data from 1979
- 15-day forecast
- Current conditions

### Pricing
| Plan | Solar Access | Cost/Month |
|------|--------------|------------|
| Free | ❌ No solar data | $0 |
| Developer | ❌ No solar data | $180 |
| **Solar Radiation** | ✅ Yes | **~$800** |
| Enterprise | ✅ Custom | Contact sales |

### Limitations
- **Very expensive** for solar data ($800/month)
- Solar data NOT included in free tier
- Requires separate subscription
- Complex pricing structure

### Best For
- **Large enterprises** with budget
- **Projects already using OpenWeather** ecosystem
- **Not recommended for individual developers**

### PVSolarSim Integration Status
✅ **Partially implemented** (generic weather, no solar radiation yet)

---

## 4. Windy.com API

**Provider:** Windy.com  
**Website:** https://api.windy.com/

### ❌ **NOT SUITABLE for Solar PV Simulation**

### Why Windy Doesn't Work
1. **No solar irradiance data** (GHI, DNI, DHI not provided)
2. Designed for **wind forecasting** and general weather
3. Missing critical PV parameters

### Data Provided
- Wind speed/direction (main focus)
- Temperature, pressure, humidity
- Clouds, precipitation
- Weather forecasts
- **❌ NO solar radiation data**

### Pricing
| Plan | Price | Calls/Day |
|------|-------|-----------|
| Free | $0 | 500 |
| Hobbyist | $10/month | 5,000 |
| Start-up | $50/month | 50,000 |
| Business | $200/month | 250,000 |

### Verdict
**Not usable for PVSolarSim** - lacks essential solar radiation data.

---

## 5. Solcast

**Provider:** Solcast Pty Ltd  
**Website:** https://solcast.com/

### ✅ **Best Accuracy for Solar PV**
- **Specialized in solar forecasting**
- Satellite-derived irradiance
- Sub-hourly resolution
- Advanced soiling models (PM2.5, PM10 integration)

### Data Provided
- GHI, DNI, DHI (all sky and clear sky)
- Sub-hourly resolution (5-30 minutes)
- Historical from 2007
- Forecasts up to 14 days
- Soiling loss estimation
- Albedo data

### Pricing
- **No free tier** for API access
- Contact sales for quote
- Typically **enterprise pricing** ($1,000+/month)
- Hobbyist tier may be available (check website)

### Best For
- **Commercial PV plants**
- **Grid integration**
- **Energy trading**
- **High-accuracy requirements**

### PVSolarSim Integration Status
⏭️ **Not planned** (too expensive for typical users)

---

## 6. Other Providers (Brief Overview)

### Xweather (formerly AerisWeather)
- Solar radiation data available
- Pricing: Pay-as-you-go (~$0.01/unit)
- Good for US locations
- Integration: ⏭️ Not planned

### SolarAnywhere
- High-quality solar data
- Global coverage
- Expensive (enterprise pricing)
- Integration: ⏭️ Not planned

### NREL NSRDB (National Solar Radiation Database)
- **FREE** for US locations
- High-quality ground station data
- Coverage: USA only
- Integration: ⏭️ Future consideration

### Meteotest (Solar Web Services)
- European focus
- High accuracy
- Expensive
- Integration: ⏭️ Not planned

---

## Comparison Matrix

| Provider | Free Tier | Solar Data | Coverage | Best For | PVSolarSim Status |
|----------|-----------|------------|----------|----------|-------------------|
| **PVGIS** | ✅ Full | ✅ Yes | 🌍 Global (focus EU) | Development, TMY | ✅ Implemented |
| **Visual Crossing** | ✅ 1000/day | ✅ Yes | 🌍 Global | Production | ⏭️ Planned |
| **OpenWeatherMap** | ❌ No solar | ✅ Yes ($$$) | 🌍 Global | Enterprise only | 🟡 Partial |
| **Windy.com** | ✅ 500/day | ❌ No | 🌍 Global | ❌ Not suitable | ❌ Not planned |
| **Solcast** | ❌ No | ✅ Yes (best) | 🌍 Global | Enterprise PV | ⏭️ Not planned |
| **NREL NSRDB** | ✅ Full | ✅ Yes | 🇺🇸 USA only | US research | ⏭️ Future |

---

## Recommendations for PVSolarSim Users

### For Development & Testing
**Use PVGIS** (already implemented):
```python
from pvsolarsim import simulate_annual, Location, PVSystem

results = simulate_annual(
    location=Location(...),
    system=PVSystem(...),
    year=2025,
    weather_source='pvgis'  # FREE!
)
```

### For Production & Real-World Validation
**Use Visual Crossing** (best value):
```python
# Free tier: 1,000 records/day
results = simulate_annual(
    location=Location(...),
    system=PVSystem(...),
    year=2025,
    weather_source='visual_crossing',  # Coming soon!
    api_key='YOUR_KEY'
)
```

**Cost for 1 year simulation:**
- Hourly data: 8,760 records = $0.88 (or free if <1000/day spread)
- Very affordable!

### For Enterprise / High Accuracy
**Use Solcast or SolarAnywhere:**
- Contact provider for pricing
- Expect $1,000+/month
- Best accuracy and support
- Custom integration needed

---

## Implementation Priorities for PVSolarSim

### Phase 1: ✅ Complete (PR #6)
- ✅ PVGIS TMY client
- ✅ CSV/JSON file readers
- ✅ Weather data caching

### Phase 2: 🔄 In Progress
- 🔄 Visual Crossing API client (highest priority)
- 🔄 Improved error handling
- 🔄 Rate limiting and retry logic

### Phase 3: ⏭️ Future
- ⏭️ NREL NSRDB client (US only)
- ⏭️ OpenWeatherMap solar API (if budget allows)
- ⏭️ Solcast integration (enterprise users)

---

## Cost Analysis: Real-World Example

**Scenario:** Annual simulation for Prague PV system (14.04 kWp)

### Option 1: PVGIS (FREE)
- Cost: **$0**
- Data: TMY 2005-2020 average
- Accuracy: Good for long-term planning
- ✅ Best for development

### Option 2: Visual Crossing (Pay-as-you-go)
- Hourly data for 2025: 8,760 records
- Cost: **$0.88** (or free if <1000/day)
- Data: Actual 2025 weather
- Accuracy: Very good
- ✅ Best for production

### Option 3: OpenWeatherMap Solar
- Cost: **$800/month** minimum
- Data: Historical + forecast
- Accuracy: Good
- ❌ Too expensive for individuals

### Option 4: Solcast
- Cost: **$1,000+/month** (estimate)
- Data: High-resolution, validated
- Accuracy: Best available
- ❌ Only for enterprise

**Winner:** Visual Crossing ($0.88/year or free tier)

---

## Frequently Asked Questions

### Q: Why doesn't Windy.com work for solar PV?
**A:** Windy specializes in **wind forecasting** and general weather. They don't provide solar irradiance data (GHI, DNI, DHI) which is essential for PV simulations.

### Q: Is OpenWeatherMap's free tier usable?
**A:** Only for basic weather (temperature, wind, cloud cover). **Solar radiation data requires ~$800/month subscription** - not suitable for individual developers.

### Q: What's the best free option?
**A:** **PVGIS** for TMY data (already in PVSolarSim), or **Visual Crossing free tier** (1,000 records/day) for actual weather.

### Q: Can I use CSV files with real data?
**A:** Yes! PVSolarSim supports CSV import:
```python
results = simulate_annual(
    ...,
    weather_source='csv',
    file_path='my_weather_data.csv',
    column_mapping={'ghi': 'irradiance', 'temp_air': 'temperature'}
)
```

### Q: How accurate is PVGIS vs real weather?
**A:** PVGIS TMY is **long-term average** (2005-2020). Actual year can vary ±30% due to weather. For validation, use actual weather from Visual Crossing.

---

## Conclusion

**For PVSolarSim users:**

1. **Use PVGIS for free** (development, testing, long-term estimates)
2. **Upgrade to Visual Crossing** ($49/month or pay-as-you-go) for production
3. **Avoid OpenWeatherMap solar API** (too expensive at $800/month)
4. **Don't use Windy.com** (no solar data)
5. **Consider Solcast** only for enterprise projects with budget

**Next Steps:**
- Implement Visual Crossing API client (highest priority)
- Add examples for different weather sources
- Document cost-benefit analysis for users

---

**Contributing:** Found a better weather provider? Open an issue or PR!

**License:** MIT (same as PVSolarSim)
