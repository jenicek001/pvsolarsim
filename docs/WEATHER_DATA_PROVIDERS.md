# Weather Data Providers for PV Solar Simulation

**Last Updated:** January 24, 2026  
**Status:** Comprehensive Analysis Complete

---

## Executive Summary

This document provides a comprehensive analysis of weather data providers suitable for photovoltaic (PV) solar energy simulation. The analysis focuses on providers that offer the critical solar irradiance data (GHI, DNI, DHI) required for accurate PV power calculations.

### Quick Recommendations

| Use Case | Recommended Provider | Why |
|----------|---------------------|-----|
| **Development & Testing** | PVGIS (FREE) | Already implemented, excellent historical data |
| **Production Applications** | Visual Crossing ($49/mo or 1000 calls/day FREE) | Best balance of cost, features, and reliability |
| **Enterprise/Commercial** | Solcast or Visual Crossing Weather | Professional-grade solar forecasting |
| **Research & Validation** | PVGIS or NSRDB | High-quality validated datasets |

### NOT Recommended

- ❌ **Windy.com** - Does NOT provide solar irradiance data (GHI, DNI, DHI)
- ❌ **OpenWeatherMap Solar API** - Too expensive (~$800/month minimum)
- ❌ **Standard weather APIs** - Most lack solar-specific irradiance components

---

## Essential Data Requirements

For accurate PV solar simulation, a weather data provider **MUST** supply:

### Critical Parameters
1. **Solar Irradiance Components** (at least one of):
   - **GHI** (Global Horizontal Irradiance) - Total solar radiation on horizontal surface
   - **DNI** (Direct Normal Irradiance) - Direct beam radiation perpendicular to sun
   - **DHI** (Diffuse Horizontal Irradiance) - Scattered radiation from sky

2. **Ambient Temperature** - Required for temperature-dependent efficiency calculations

### Highly Desirable Parameters
- **Wind Speed** - For advanced thermal modeling
- **Cloud Cover** - For irradiance modeling and forecasting
- **Relative Humidity** - For atmospheric modeling
- **Air Pressure** - For atmospheric corrections

---

## Provider Comparison Matrix

| Provider | Solar Data | Cost | Historical | Forecast | TMY | API Quality | Recommendation |
|----------|-----------|------|------------|----------|-----|-------------|----------------|
| **PVGIS** | ✅ GHI, DNI, DHI | FREE | ✅ 2005-2020 | ❌ No | ✅ Yes | ⭐⭐⭐⭐⭐ | ✅ **Recommended** |
| **Visual Crossing** | ✅ GHI, DNI | $49/mo or 1000/day FREE | ✅ 1970-present | ✅ 15 days | ✅ Yes | ⭐⭐⭐⭐⭐ | ✅ **Recommended** |
| **Solcast** | ✅ GHI, DNI, DHI | $500-2000+/mo | ✅ Limited | ✅ 7-14 days | ❌ No | ⭐⭐⭐⭐⭐ | ⚠️ Enterprise only |
| **NSRDB (NREL)** | ✅ GHI, DNI, DHI | FREE (USA only) | ✅ 1998-2021 | ❌ No | ✅ Yes | ⭐⭐⭐⭐ | ⚠️ USA locations only |
| **OpenWeatherMap Solar** | ✅ GHI, DNI, DHI | ~$800/mo | ✅ Yes | ✅ 5 days | ❌ No | ⭐⭐⭐⭐ | ⚠️ Too expensive |
| **Windy.com** | ❌ **NO** | $10-200/mo | ✅ Yes | ✅ 10 days | ❌ No | ⭐⭐⭐ | ❌ **NOT suitable** |
| **Tomorrow.io** | ⚠️ GHI only | $49-299/mo | ✅ Limited | ✅ 15 days | ❌ No | ⭐⭐⭐ | ⚠️ Limited solar data |
| **WeatherAPI.com** | ⚠️ Limited | $0-149/mo | ✅ Yes | ✅ 14 days | ❌ No | ⭐⭐⭐ | ⚠️ Insufficient solar data |

---

## Detailed Provider Analysis

### 1. PVGIS (Photovoltaic Geographical Information System)

**Website:** https://re.jrc.ec.europa.eu/pvgis/  
**Provider:** European Commission Joint Research Centre  
**Status:** ✅ **ALREADY IMPLEMENTED** in PVSolarSim

#### ✅ Strengths
- **FREE** with no API key required
- High-quality validated solar radiation data
- Excellent global coverage (except some polar regions)
- Typical Meteorological Year (TMY) data available
- Multiple radiation databases (PVGIS-SARAH2, PVGIS-NSRDB, etc.)
- Reliable and stable API
- No rate limits for reasonable use
- Perfect for development and validation

#### ❌ Limitations
- No real-time or forecast data (historical only)
- Limited to past 15-20 years (database dependent)
- Coarse temporal resolution (hourly or daily)
- Some regions have limited data coverage

#### 💰 Cost
- **FREE**
- No registration required
- Unlimited reasonable use

#### 📊 Data Quality
- ⭐⭐⭐⭐⭐ Excellent
- Validated against ground measurements
- Used by solar industry worldwide

#### 🔧 PVSolarSim Integration
```python
from pvsolarsim.weather import PVGISClient

client = PVGISClient()
weather_data = client.get_tmy_data(
    latitude=40.0,
    longitude=-105.0,
    outputformat='json'
)
```

**Status:** ✅ Fully implemented and tested

---

### 2. Visual Crossing Weather

**Website:** https://www.visualcrossing.com/  
**Status:** 🔄 **RECOMMENDED FOR WEEK 11 IMPLEMENTATION**

#### ✅ Strengths
- Comprehensive solar data (GHI, DNI)
- Excellent historical coverage (1970-present)
- 15-day weather forecast included
- **1000 API calls/day FREE tier** (perfect for development)
- High-quality unified weather API
- Global coverage with good data density
- Hourly and daily resolution
- CSV, JSON, and other formats
- Good documentation and support

#### ❌ Limitations
- Paid tier needed for production use (>1000 calls/day)
- No DHI component (can be calculated)
- Forecast solar data less accurate than specialized providers

#### 💰 Cost
- **FREE Tier:** 1000 calls/day (perfect for development/testing)
- **Standard:** $49/month (100,000 calls)
- **Premium:** $249/month (500,000 calls)
- **Enterprise:** Custom pricing

**Cost-Effectiveness:** ⭐⭐⭐⭐⭐ Excellent (FREE tier + reasonable paid options)

#### 📊 Data Quality
- ⭐⭐⭐⭐⭐ Excellent
- Combines multiple weather models
- Good validation against measurements

#### 🔧 Planned PVSolarSim Integration (Week 11)
```python
from pvsolarsim.weather import VisualCrossingClient

client = VisualCrossingClient(api_key="YOUR_API_KEY")
weather_data = client.get_historical_data(
    latitude=40.0,
    longitude=-105.0,
    start_date="2025-01-01",
    end_date="2025-12-31"
)
```

**Status:** 📋 Planned for Week 11 implementation

---

### 3. Solcast

**Website:** https://solcast.com/  
**Provider:** Professional solar forecasting service

#### ✅ Strengths
- **Best-in-class solar forecasting**
- Full irradiance components (GHI, DNI, DHI)
- Real-time and forecast data
- Optimized for PV applications
- Probabilistic forecasts (P10, P50, P90)
- 7-14 day forecasts
- Satellite-derived data
- Industry-standard for commercial solar

#### ❌ Limitations
- **Expensive** - Starts at $500+/month
- Overkill for development/hobby projects
- Requires commercial account

#### 💰 Cost
- **Hobby:** FREE (very limited, 10 API calls/day)
- **Professional:** $500-1000/month
- **Enterprise:** $2000+/month

**Cost-Effectiveness:** ⭐⭐ (Only for commercial/enterprise use)

#### 📊 Data Quality
- ⭐⭐⭐⭐⭐ Industry-leading
- Satellite-based with ML enhancements
- Widely used in solar industry

#### 🔧 PVSolarSim Integration
**Status:** ⏸️ Not planned due to high cost (enterprise users can implement custom integration)

---

### 4. NSRDB (National Solar Radiation Database)

**Website:** https://nsrdb.nrel.gov/  
**Provider:** NREL (National Renewable Energy Laboratory)

#### ✅ Strengths
- **FREE** for USA locations
- Extremely high quality validated data
- Full irradiance components (GHI, DNI, DHI)
- Half-hourly resolution
- Long historical period (1998-2021)
- TMY datasets available
- Excellent for research and validation

#### ❌ Limitations
- **USA ONLY** (Americas in some datasets)
- No forecast data (historical only)
- Registration required
- Data download (not real-time API)

#### 💰 Cost
- **FREE** with registration
- No commercial restrictions

#### 📊 Data Quality
- ⭐⭐⭐⭐⭐ Gold standard
- Ground-validated
- Research-grade accuracy

#### 🔧 PVSolarSim Integration
**Status:** ⏸️ Possible future integration (manual CSV download workflow currently)

---

### 5. OpenWeatherMap Solar Radiation API

**Website:** https://openweathermap.org/api/solar-radiation  
**Status:** ⚠️ **TOO EXPENSIVE**

#### ✅ Strengths
- Full solar irradiance data (GHI, DNI, DHI)
- Historical and forecast data
- Global coverage
- Professional-grade API
- Good documentation

#### ❌ Limitations
- **VERY EXPENSIVE** - Minimum ~$800/month for "Solar Energy Prediction" plan
- No free tier with solar data
- Overkill for most applications

#### 💰 Cost
- **Solar Energy Prediction:** ~$800-1000/month (minimum)
- FREE tier does NOT include solar radiation data

**Cost-Effectiveness:** ⭐ Poor (too expensive for individual/small business use)

#### 📊 Data Quality
- ⭐⭐⭐⭐ Very Good
- Modeled data with satellite validation

#### 🔧 PVSolarSim Integration
**Status:** ❌ Not planned due to prohibitive cost

---

### 6. Windy.com API

**Website:** https://www.windy.com/  
**Status:** ❌ **NOT SUITABLE** for PV Solar Simulation

#### ⚠️ Critical Issue
**Windy.com does NOT provide solar irradiance data (GHI, DNI, DHI)**

The API focuses on:
- Wind speed and direction (primary focus)
- Temperature, pressure, humidity
- Cloud cover
- Precipitation
- But **NO solar-specific irradiance components**

#### Why It Doesn't Work
Without GHI, DNI, or DHI data, it's **impossible** to calculate PV power output accurately. While cloud cover can be used for rough estimation, it cannot replace direct solar irradiance measurements.

#### 💰 Cost
- Point Forecast: $10/month (50 calls/day)
- Premium: $100/month (1000 calls/day)
- Enterprise: $200/month (10,000 calls/day)

#### 📊 Data Quality
- ⭐⭐⭐ Good for wind forecasting
- ❌ Unusable for solar PV (missing critical data)

#### 🔧 PVSolarSim Integration
**Status:** ❌ **NOT RECOMMENDED** - Cannot be used for PV simulation

**Conclusion:** Windy.com is excellent for wind energy forecasting but fundamentally incompatible with solar PV simulation requirements.

---

### 7. Tomorrow.io (formerly ClimaCell)

**Website:** https://www.tomorrow.io/

#### ✅ Strengths
- GHI data available
- Good forecast accuracy
- 15-day forecasts
- Hyperlocal weather data
- Modern API

#### ❌ Limitations
- **Missing DNI and DHI** - Only GHI available
- Limited solar-specific features
- More expensive than Visual Crossing

#### 💰 Cost
- **Free:** 500 calls/day (limited fields)
- **Essential:** $49/month
- **Professional:** $299/month

**Cost-Effectiveness:** ⭐⭐⭐ Moderate

#### 📊 Data Quality
- ⭐⭐⭐ Good
- GHI only limits accuracy

#### 🔧 PVSolarSim Integration
**Status:** ⏸️ Possible future integration if DNI/DHI added

---

### 8. WeatherAPI.com

**Website:** https://www.weatherapi.com/

#### ✅ Strengths
- Affordable pricing
- Historical and forecast data
- Global coverage

#### ❌ Limitations
- **Very limited solar data** - No GHI, DNI, or DHI
- Only provides UV index and generic solar radiation
- Insufficient for PV calculations

#### 💰 Cost
- **Free:** 1M calls/month (limited features)
- **Pro:** $9-149/month

#### 📊 Data Quality
- ⭐⭐ Poor for solar applications

#### 🔧 PVSolarSim Integration
**Status:** ❌ Not suitable - missing critical solar data

---

## Implementation Roadmap

### ✅ Currently Implemented

#### PVGIS Integration (Week 9-10)
- Fully functional PVGIS API client
- TMY data retrieval
- Multiple radiation databases supported
- Comprehensive error handling
- Test coverage: >85%

**Files:**
- `src/pvsolarsim/weather/api_clients.py`
- `tests/test_weather_api_clients.py`
- `examples/weather_api_example.py`

---

### 🔄 Week 11 Priority: Visual Crossing Integration

**Implementation Plan:**

#### Phase 1: API Client (Week 11, Day 1-2)
```python
# src/pvsolarsim/weather/api_clients.py

class VisualCrossingClient(WeatherAPIClient):
    """Visual Crossing Weather API client for solar data."""
    
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    
    def get_historical_data(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        include_solar: bool = True
    ) -> pd.DataFrame:
        """Fetch historical weather data with solar irradiance."""
        pass
    
    def get_forecast_data(
        self,
        latitude: float,
        longitude: float,
        days: int = 15
    ) -> pd.DataFrame:
        """Fetch weather forecast with solar predictions."""
        pass
```

#### Phase 2: Testing (Week 11, Day 3)
- Unit tests for API client
- Integration tests with real API calls (skip in CI)
- Validation against PVGIS data

#### Phase 3: Documentation (Week 11, Day 4)
- Update WEATHER_DATA_GUIDE.md
- Add example scripts
- Document API key setup

#### Phase 4: Integration (Week 11, Day 5)
- Integrate with simulation engine
- Add to weather data selection options
- Update examples

**Success Criteria:**
- [ ] Visual Crossing client implemented
- [ ] Tests passing (>90% coverage)
- [ ] Documentation complete
- [ ] Example working with FREE tier API key

---

### ⏸️ Future Considerations

#### Solcast Integration
- Only if enterprise sponsors request it
- High cost makes it unsuitable for general use
- Can be implemented as plugin

#### NSRDB Integration
- Useful for USA-based validation
- Manual CSV workflow currently sufficient
- API integration if demand exists

#### Custom Data Import
- Already supported via CSV readers
- Users can import from any source

---

## Best Practices for Weather Data Selection

### Development & Testing
**Use:** PVGIS (FREE) or Visual Crossing FREE tier
- No cost
- Good data quality
- Sufficient for development

### Production Applications
**Use:** Visual Crossing ($49/mo)
- Best balance of cost and features
- Historical + forecast data
- Reliable API

### Research & Validation
**Use:** PVGIS or NSRDB (both FREE)
- Highest quality validated data
- TMY datasets
- Long historical records

### Commercial/Enterprise Solar
**Consider:** Solcast
- Best solar forecasting accuracy
- Professional-grade features
- Worth the investment for commercial operations

---

## Data Format Standardization

All weather API clients in PVSolarSim return data in a standardized pandas DataFrame format:

```python
# Required columns
- 'temp_air': Ambient air temperature (°C)
- 'ghi': Global Horizontal Irradiance (W/m²)

# Optional columns (provider-dependent)
- 'dni': Direct Normal Irradiance (W/m²)
- 'dhi': Diffuse Horizontal Irradiance (W/m²)
- 'wind_speed': Wind speed (m/s)
- 'cloud_cover': Cloud coverage (0-100%)

# Index: pd.DatetimeIndex (timezone-aware)
```

**Missing Components:**
If a provider doesn't supply all irradiance components, PVSolarSim can:
1. Use clear-sky model to estimate missing components
2. Use decomposition models (e.g., DISC model for DNI from GHI)
3. Apply empirical correlations

---

## Conclusion

### Top Recommendations

1. **PVGIS** (✅ Already implemented) - Perfect for development and validation
2. **Visual Crossing** (🔄 Week 11 priority) - Best for production applications
3. **Avoid Windy.com** (❌) - Does not provide solar irradiance data

### Implementation Status

- ✅ PVGIS: Fully functional
- 🔄 Visual Crossing: Planned for Week 11
- ⏸️ Others: On hold pending user demand

### Next Steps

1. Complete Visual Crossing integration (Week 11)
2. Add data source comparison examples
3. Document best practices for each use case
4. Monitor user feedback for additional providers

---

**Document Version:** 1.0  
**Author:** PVSolarSim Development Team  
**Last Review:** January 24, 2026

For questions or suggestions, please open an issue on GitHub:
https://github.com/jenicek001/pvsolarsim/issues
