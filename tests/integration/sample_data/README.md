# Prague PV Installation - Technical Specifications

This directory contains sample weather data and documentation for a **real-world photovoltaic installation in Prague, Czech Republic**. All parameters are actual specifications from the installed system and should be used for validation testing.

---

## 📍 Location

- **Latitude:** 50.0807494°N
- **Longitude:** 14.8594164°E
- **Altitude:** 220 meters above sea level ⚠️ *(NOT 300m - use correct value)*
- **Timezone:** Europe/Prague (CET/CEST)
- **Climate Zone:** Temperate continental (Cfb - Köppen classification)

---

## 🏠 Installation Details

### Roof Orientation
- **Tilt Angle:** 35° (optimal for Central European latitude)
- **Azimuth:** 202° (South-Southwest, SSW)
- **Mounting:** Roof-mounted, fixed tilt
- **Shading:** Minimal (open southern exposure)

---

## ☀️ Panel Specifications

### String 1: München Energieprodukte MSMD450M6-72 M6
- **Quantity:** 16 panels
- **Power per Panel:** 450 Wp (STC)
- **Total String Power:** 7,200 Wp (7.2 kWp)
- **Module Dimensions:** 2.108 m × 1.048 m = 2.209 m² each
- **Total Area (String 1):** 35.344 m²
- **Cell Technology:** Monocrystalline half-cut (144 cells)
- **Module Efficiency:** 20.37%
- **Temperature Coefficient:** -0.35%/°C
- **STC Voltage (Vmp):** ~41.5V
- **STC Current (Imp):** ~10.8A

### String 2: Canadian Solar HiKu CS3L-380MS
- **Quantity:** 18 panels
- **Power per Panel:** 380 Wp (STC)
- **Total String Power:** 6,840 Wp (6.84 kWp)
- **Module Dimensions:** 1.765 m × 1.048 m = 1.850 m² each
- **Total Area (String 2):** 33.30 m²
- **Cell Technology:** Monocrystalline PERC (120 cells)
- **Module Efficiency:** 20.5%
- **Temperature Coefficient:** -0.37%/°C
- **STC Voltage (Vmp):** ~38.2V
- **STC Current (Imp):** ~9.95A

### System Totals
- **Total Installed Capacity:** 14.04 kWp (14,040 Wp)
- **Total Panel Area:** 68.64 m²
- **Weighted Average Efficiency:** 20.45%
- **Weighted Temperature Coefficient:** -0.360%/°C
- **Total Number of Panels:** 34 panels
- **System Configuration:** 2 strings (MPPT1: 16×450W, MPPT2: 18×380W)

---

## ⚡ Expected Performance

### Annual Energy Production
- **Specific Yield:** 900-1,100 kWh/kWp per year (Central Europe average)
- **Total Annual Production:** 12,600-15,400 kWh/year
- **Daily Average (Annual):** 34.5-42.2 kWh/day
- **Capacity Factor:** ~12-15% (typical for Czech Republic)

### Seasonal Expectations
- **Winter (Dec-Feb):** 15-25 kWh/day average, peak ~6-8 kW
- **Spring (Mar-May):** 35-50 kWh/day average, peak ~10-12 kW
- **Summer (Jun-Aug):** 50-70 kWh/day average, peak ~12-14 kW
- **Autumn (Sep-Nov):** 25-40 kWh/day average, peak ~9-11 kW

### Performance Ratio
- **Expected PR:** 75-85% (industry standard for well-maintained systems)
- **Losses Accounted:**
  - Temperature losses: ~5-10%
  - Soiling/dust: ~2-3%
  - Inverter efficiency: ~3-4%
  - Cable losses: ~1-2%
  - Mismatch losses: ~1-2%

---

## 📊 Weather Data Files

### File: `prague_weather_2025_sample.csv`

**Dataset Summary:**
- **Total Records:** 96 hourly measurements
- **Date Range:** 2024-12-31 23:00:00 UTC to 2025-10-01 21:00:00 UTC
- **Temporal Resolution:** 1 hour
- **Representative Days:** Sample days from each season (Jan, Apr, Jul, Oct)

**Data Structure:**
```csv
timestamp,ghi,dni,dhi,temp_air,wind_speed,cloud_cover
2024-12-31 23:00:00+00:00,0,0,0,2.0,3.5,80
2025-01-01 00:00:00+00:00,0,0,0,1.8,3.2,75
...
```

**Column Specifications:**
- `timestamp`: ISO 8601 format with UTC timezone (YYYY-MM-DD HH:MM:SS+00:00)
- `ghi`: Global Horizontal Irradiance (W/m²) - range 0-1200
- `dni`: Direct Normal Irradiance (W/m²) - range 0-1000
- `dhi`: Diffuse Horizontal Irradiance (W/m²) - range 0-500
- `temp_air`: Ambient air temperature (°C) - typical range -20 to 35
- `wind_speed`: Wind speed at 10m height (m/s) - range 0-15
- `cloud_cover`: Cloud cover fraction (0-100) - 0=clear, 100=overcast

**Representative Days:**
1. **January 1, 2025 (Winter):**
   - Typical cloudy winter day
   - Low irradiance: GHI peak ~200-300 W/m²
   - Cold temperature: -2 to 4°C
   - Expected production: ~25-35 kWh/day

2. **April 1, 2025 (Spring):**
   - Mixed conditions (partial clouds)
   - Moderate irradiance: GHI peak ~600-800 W/m²
   - Mild temperature: 8 to 15°C
   - Expected production: ~40-55 kWh/day

3. **July days (Summer):**
   - Clear to partly cloudy
   - High irradiance: GHI peak 900-1100 W/m²
   - Warm temperature: 20 to 30°C
   - Expected production: ~60-75 kWh/day

4. **October 1, 2025 (Autumn):**
   - Variable conditions
   - Moderate irradiance: GHI peak ~400-600 W/m²
   - Cool temperature: 10 to 18°C
   - Expected production: ~30-45 kWh/day

---

## 🔬 Validation Benchmarks

### Expected Accuracy vs. pvlib-python

When comparing PVSolarSim results to pvlib-python (industry standard):

**Solar Position:**
- Azimuth error: < 0.1° MAE (Mean Absolute Error)
- Elevation error: < 0.1° MAE
- Valid for all solar elevations > 0°

**Clear-Sky Irradiance:**
- GHI error: < 5% MAPE (Mean Absolute Percentage Error)
- DNI error: < 5% MAPE
- DHI error: < 10% MAPE (diffuse is harder to model)

**POA Irradiance:**
- POA Global error: < 3% MAPE for solar elevation > 10°
- POA Direct error: < 5% MAPE
- POA Diffuse error: < 10% MAPE

**Cell Temperature:**
- Temperature error: < 1°C MAE (all models)
- Valid for irradiance > 100 W/m² and wind speed 0-10 m/s

**Power Output:**
- Instantaneous power error: < 5% MAPE
- Daily energy error: < 3% for well-characterized systems
- Annual energy error: < 5% with validated weather data

---

## 📝 Usage in Tests

### Standard Test Configuration

When writing integration tests for this system, use these constants:

```python
# Location
LATITUDE = 50.0807494
LONGITUDE = 14.8594164
ALTITUDE = 220  # meters ⚠️ NOT 300!
TIMEZONE = "Europe/Prague"

# Panel String 1 (München)
MUNICH_PANELS = 16
MUNICH_POWER = 450  # Wp per panel
MUNICH_AREA = 2.209  # m² per panel
MUNICH_EFFICIENCY = 0.2037
MUNICH_TEMP_COEFF = -0.0035  # per °C

# Panel String 2 (Canadian Solar)
CANADIAN_PANELS = 18
CANADIAN_POWER = 380  # Wp per panel
CANADIAN_AREA = 1.850  # m² per panel
CANADIAN_EFFICIENCY = 0.205
CANADIAN_TEMP_COEFF = -0.0037  # per °C

# System Totals
TOTAL_AREA = 68.64  # m²
TOTAL_POWER = 14040  # Wp (14.04 kWp)
WEIGHTED_EFFICIENCY = 0.2045
WEIGHTED_TEMP_COEFF = -0.00360  # per °C

# Orientation
TILT = 35  # degrees
AZIMUTH = 202  # degrees (SSW)

# Weather Data
WEATHER_FILE = "tests/integration/sample_data/prague_weather_2025_sample.csv"
```

### Validation Thresholds

Use these thresholds when asserting test results:

```python
# Solar position tolerance
AZIMUTH_TOLERANCE = 0.1  # degrees
ELEVATION_TOLERANCE = 0.1  # degrees

# Irradiance tolerance (for solar elevation > 10°)
GHI_TOLERANCE_PERCENT = 5  # %
POA_TOLERANCE_PERCENT = 3  # %

# Temperature tolerance
TEMP_TOLERANCE = 1.0  # °C

# Power tolerance
POWER_TOLERANCE_PERCENT = 5  # %

# Energy tolerance (daily/annual)
ENERGY_TOLERANCE_PERCENT = 3  # %
```

---

## 🌍 Prague Climate Context

### Typical Conditions
- **Annual Sunshine Hours:** ~1,600-1,800 hours
- **Average Annual Temperature:** 9-10°C
- **Average Summer Temperature:** 18-20°C (Jun-Aug)
- **Average Winter Temperature:** -1 to 1°C (Dec-Feb)
- **Annual Precipitation:** ~500-600 mm
- **Snow Days:** 20-30 days per year (Dec-Mar)

### Solar Resource
- **Global Horizontal Irradiation (GHI):** ~1,050-1,150 kWh/m²/year
- **Direct Normal Irradiation (DNI):** ~1,100-1,200 kWh/m²/year
- **Optimal Tilt Irradiation (35°):** ~1,200-1,300 kWh/m²/year
- **Peak Sun Hours:** ~3.0-3.2 hours/day (annual average)

### Seasonal Irradiation Distribution
- **Winter (Dec-Feb):** ~10-12% of annual total
- **Spring (Mar-May):** ~28-30% of annual total
- **Summer (Jun-Aug):** ~40-42% of annual total
- **Autumn (Sep-Nov):** ~18-20% of annual total

---

## 🔧 Maintenance Factors

### Degradation
- **Annual Degradation:** ~0.5-0.7% per year (typical for monocrystalline)
- **25-Year Performance:** ~80-85% of original capacity
- **Linear Degradation Model:** `efficiency(year) = efficiency_0 * (1 - 0.006 * year)`

### Soiling
- **Urban Environment:** ~2-5% annual losses (Prague)
- **Cleaning Frequency:** Rain + 1-2 manual cleanings per year
- **Seasonal Variation:** Higher in spring (pollen) and autumn (leaves)
- **Soiling Factor:** 0.95-0.98 (95-98% transmission)

### Inverter Efficiency
- **European Efficiency:** ~96-98% (modern inverters)
- **MPPT Efficiency:** ~99.5%
- **Nighttime Consumption:** ~1-3W (standby)

---

## 🔍 Test Validation Checklist

When validating simulation results, ensure:

- [ ] Solar position errors < 0.1° for all daytime hours
- [ ] POA irradiance within 3% of pvlib for elevation > 10°
- [ ] Cell temperature within 1°C of pvlib (Faiman model)
- [ ] Daily energy production realistic for season:
  - Winter: 15-35 kWh/day
  - Spring: 35-55 kWh/day
  - Summer: 50-75 kWh/day
  - Autumn: 25-45 kWh/day
- [ ] Peak power < rated capacity (14.04 kW) × 1.1 safety margin
- [ ] No power generation when solar elevation < 0°
- [ ] Temperature derating applied (< 100% efficiency when hot)
- [ ] Annual specific yield: 900-1,100 kWh/kWp

---

## 📚 References

1. **PVGIS Database:** EU Joint Research Centre solar radiation database
   - Historical data: https://re.jrc.ec.europa.eu/pvg_tools/en/
   - TMY data available for Prague coordinates

2. **Czech Solar Association:** National PV statistics
   - Average specific yield: 950-1,050 kWh/kWp/year (Czech Republic)
   - Performance ratio: 80-85% (well-maintained systems)

3. **pvlib-python Documentation:** Validation reference
   - Solar position: NREL SPA algorithm (±0.0003° accuracy)
   - Clear-sky models: Ineichen, Simplified Solis
   - Temperature models: Faiman, SAPM, PVsyst

---

**Last Updated:** December 29, 2025  
**Maintained by:** PVSolarSim Development Team  
**System Owner:** Real installation in Prague

**For Questions:** Refer to test_pr8.py for usage examples
- Moderate radiation: Peak ~762 W/m² GHI
- Mild temperatures: 6°C to 18°C
- Medium cloud cover: 37-70%
- Longer daylight: ~13 hours

### Summer (July)
- High radiation: Peak ~925 W/m² GHI
- Warm temperatures: 16.5°C to 28.8°C
- Low cloud cover: 20-48%
- Long daylight: ~15 hours

### Autumn (October)
- Moderate radiation: Peak ~612 W/m² GHI
- Cool temperatures: 8°C to 17°C
- Medium-high cloud cover: 47-71%
- Shorter daylight: ~11 hours

## Expected Annual Yields

For a 14.04 kWp system (like the one in test_pr5.py) with this weather data, expected annual energy production would be:

- **With real Prague weather:** ~11,000-13,000 kWh/year (780-930 kWh/kWp)
- **Industry benchmark for Prague:** ~850-1,100 kWh/kWp/year for south-facing systems
- **With optimal conditions (clear sky):** ~20,000+ kWh/year (theoretical maximum)

## Usage

These files are used by integration tests to validate weather data loading functionality:

```python
from pvsolarsim import simulate_annual
from pvsolarsim.weather import CSVWeatherReader

# Load from CSV
weather_data = CSVWeatherReader('prague_weather_2025_sample.csv')
results = simulate_annual(
    location=location,
    system=system,
    weather_data=weather_data
)
```

## Data Sources

This sample data is synthetically generated based on:
- PVGIS database (EU JRC)
- Czech Hydrometeorological Institute long-term averages
- Typical Meteorological Year (TMY) data for Central Europe
- Physical solar radiation models

**Note:** This is sample data for testing purposes. For production simulations, use real weather data from PVGIS, NASA POWER, or local meteorological stations.
