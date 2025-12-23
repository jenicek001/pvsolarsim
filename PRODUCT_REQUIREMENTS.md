# Product Requirements Specification
## PVSolarSim Python Library

**Version:** 1.0  
**Date:** December 23, 2025  
**Status:** Draft

---

## 1. Executive Summary

### 1.1 Purpose
PVSolarSim is a comprehensive Python library designed to calculate maximum theoretical instantaneous photovoltaic (PV) power output and simulate annual energy production from solar installations. The library provides accurate physics-based modeling that accounts for geographic location, atmospheric conditions, panel characteristics, and weather patterns.

### 1.2 Project Goals
- Provide accurate instantaneous PV power output calculations
- Enable annual energy production simulations with high temporal resolution (5-minute intervals)
- Support comprehensive atmospheric and environmental modeling
- Deliver a well-documented, PyPI-ready Python package
- Ensure ease of integration with existing solar energy workflows

### 1.3 Target Users
- Solar energy system designers and engineers
- Renewable energy consultants
- Academic researchers in photovoltaic systems
- Energy analysts and data scientists
- PV system operators and maintenance personnel

---

## 2. Market Analysis

### 2.1 Existing Solutions Analysis

#### **pvlib-python** (Primary Reference)
- **Strengths:**
  - Comprehensive solar position calculations
  - Multiple clear-sky irradiance models (Ineichen, Simplified Solis, Bird, Haurwitz)
  - Atmospheric modeling with Linke turbidity, AOD, precipitable water
  - Temperature coefficient modeling
  - Wide adoption in research and industry
  - Excellent documentation and community support
  
- **Limitations:**
  - Steep learning curve for beginners
  - Requires manual integration of weather data
  - Complex API for simple use cases
  - Limited built-in annual simulation workflows

#### **PySAM** (NREL System Advisor Model)
- **Strengths:**
  - Complete system modeling including financial analysis
  - Direct integration with NREL databases
  - Industry-standard validation
  
- **Limitations:**
  - Heavy dependency on SAM core
  - More complex than needed for pure power estimation
  - Primarily focused on system-level analysis

#### **Weather Data APIs**
- **OpenWeatherMap Solar API:** GHI, DNI, DHI data with historical and forecast
- **Solcast:** High-resolution solar irradiance data (commercial)
- **PVGIS:** Free TMY and historical data for Europe and beyond

### 2.2 Market Gap
Current solutions lack:
1. **Unified simple interface** for instantaneous power calculations
2. **Built-in weather integration** with automatic cloud cover consideration
3. **Out-of-the-box annual simulation** capabilities
4. **Modern Python packaging** standards (type hints, async support, etc.)
5. **Easy-to-use API** for non-experts

---

## 3. Functional Requirements

### 3.1 Core Calculation Engine

#### FR-1: Solar Position Calculation
- **Priority:** Critical
- **Description:** Calculate sun position (azimuth, zenith, elevation) for any GPS coordinates and timestamp
- **Inputs:**
  - Latitude (decimal degrees)
  - Longitude (decimal degrees)
  - Timestamp (datetime with timezone)
  - Altitude/elevation (meters above sea level)
- **Outputs:**
  - Solar azimuth angle (degrees)
  - Solar zenith angle (degrees)
  - Solar elevation angle (degrees)
  - Hour angle (degrees)
  - Declination (degrees)
- **Dependencies:** Leverage pvlib.solarposition or implement SPA algorithm

#### FR-2: Atmospheric Attenuation Modeling
- **Priority:** Critical
- **Description:** Calculate irradiance reduction due to atmospheric effects
- **Parameters:**
  - Air mass calculation (relative and absolute)
  - Aerosol Optical Depth (AOD) at 700nm
  - Precipitable water (cm)
  - Linke turbidity factor
  - Atmospheric pressure (Pa)
  - Altitude correction
- **Models to Implement:**
  - Simplified Solis clear-sky model
  - Ineichen clear-sky model
  - Bird clear-sky model (optional, for validation)
- **Outputs:**
  - Global Horizontal Irradiance (GHI) - W/m²
  - Direct Normal Irradiance (DNI) - W/m²
  - Diffuse Horizontal Irradiance (DHI) - W/m²

#### FR-3: Cloud Cover Integration
- **Priority:** Critical
- **Description:** Adjust clear-sky irradiance based on cloud coverage
- **Inputs:**
  - Clear-sky irradiance (GHI, DNI, DHI)
  - Cloud cover percentage (0-100%)
  - Cloud type (optional: low, medium, high)
- **Method:** 
  - Implement Campbell-Norman cloud cover to irradiance model
  - Support custom attenuation factors
- **Output:** 
  - Actual irradiance under cloudy conditions

#### FR-4: Plane-of-Array (POA) Irradiance
- **Priority:** Critical
- **Description:** Calculate irradiance on tilted PV panel surface
- **Inputs:**
  - DNI, DHI, GHI from atmosphere model
  - Panel tilt angle (degrees from horizontal, 0-90°)
  - Panel azimuth orientation (degrees, 0° = North, 90° = East, 180° = South, 270° = West)
  - Solar position (azimuth, zenith)
  - Ground albedo (reflectivity, 0-1)
- **Components:**
  - Direct beam irradiance component
  - Sky diffuse irradiance (multiple models: isotropic, Hay-Davies, Perez, Klucher, Reindl)
  - Ground-reflected irradiance
- **Outputs:**
  - POA global irradiance (W/m²)
  - POA direct irradiance (W/m²)
  - POA diffuse irradiance (W/m²)
  - POA ground-reflected irradiance (W/m²)
  - Angle of incidence (AOI) (degrees)

#### FR-5: Temperature Effects on Panel Performance
- **Priority:** Critical
- **Description:** Calculate panel temperature and performance degradation
- **Inputs:**
  - Ambient air temperature (°C)
  - Wind speed (m/s)
  - POA irradiance (W/m²)
  - Module mounting configuration (rack-mounted, building-integrated, etc.)
  - Nominal Operating Cell Temperature (NOCT)
- **Calculation:**
  - Cell/module temperature estimation (Faiman, SAPM, or King models)
  - Power temperature coefficient (%/°C, typically -0.3% to -0.5%/°C)
  - Temperature-corrected efficiency
- **Outputs:**
  - Estimated cell temperature (°C)
  - Temperature correction factor (dimensionless, <1)

#### FR-6: Effective Panel Area Calculation
- **Priority:** Critical
- **Description:** Calculate effective irradiance-receiving area based on incident angle
- **Inputs:**
  - Panel area (m²)
  - Angle of incidence (AOI)
  - Incidence Angle Modifier (IAM) model parameters
- **Methods:**
  - Cosine projection for direct irradiance
  - IAM modeling (ASHRAE, Physical, Martin-Ruiz, Sapm)
  - Account for reflection losses at high incident angles
- **Output:**
  - Effective area factor (0-1)
  - IAM coefficient

#### FR-7: Instantaneous Power Calculation
- **Priority:** Critical
- **Description:** Calculate theoretical maximum DC power output
- **Formula:**
  ```
  P_dc = POA_effective * Panel_Area * Efficiency * Temp_Factor * IAM
  ```
- **Inputs:**
  - Effective POA irradiance (W/m²)
  - Total panel area (m²)
  - Panel efficiency at STC (%, standard test conditions: 25°C, 1000 W/m²)
  - Temperature correction factor
  - IAM coefficient
  - Soiling/degradation factor (optional, default 1.0)
- **Output:**
  - Maximum theoretical DC power (W)
  - Specific power output (W/m² or W/Wp)

### 3.2 Annual Simulation

#### FR-8: Time Series Simulation
- **Priority:** High
- **Description:** Simulate power output over extended periods with configurable intervals
- **Capabilities:**
  - Generate time series from start date to end date
  - Configurable time intervals (1-min, 5-min, 15-min, hourly)
  - Timezone-aware calculations
  - Daylight hours filtering (optional)
- **Inputs:**
  - Simulation start date/time
  - Simulation end date/time
  - Time step interval
  - All parameters from FR-1 through FR-7
- **Outputs:**
  - Time-indexed power output series (DataFrame)
  - Aggregated statistics (daily, monthly, annual totals)

#### FR-9: Weather Data Integration
- **Priority:** High
- **Description:** Integrate with weather data APIs for realistic simulations
- **Supported Sources:**
  - OpenWeatherMap API (solar irradiance, cloud cover, temperature, wind)
  - PVGIS TMY data
  - CSV/JSON file import (custom format support)
  - Manual input (for theoretical scenarios)
- **Data Requirements:**
  - Temperature (°C)
  - Cloud cover (%)
  - Wind speed (m/s)
  - Optional: GHI, DNI, DHI (if available, skip clear-sky calculation)
- **Features:**
  - Automatic API requests with rate limiting
  - Data caching for repeated simulations
  - Interpolation for missing data points

#### FR-10: Statistical Analysis
- **Priority:** Medium
- **Description:** Provide comprehensive statistical outputs for simulation results
- **Metrics:**
  - Total energy production (kWh, MWh)
  - Average daily/monthly/annual production
  - Peak power output and timestamp
  - Capacity factor (actual energy / theoretical maximum)
  - Performance ratio
  - Energy distribution by time of day/month
  - Percentile analysis (P50, P90, P99)
- **Outputs:**
  - Summary statistics dictionary
  - Exportable reports (JSON, CSV, PDF)

### 3.3 Advanced Features

#### FR-11: Multi-Location Comparison
- **Priority:** Low
- **Description:** Compare energy production across multiple locations simultaneously
- **Use Case:** Site selection, portfolio optimization
- **Outputs:** Comparative analysis report

#### FR-12: Shade Analysis (Future Enhancement)
- **Priority:** Low
- **Description:** Account for nearby obstructions (buildings, trees)
- **Inputs:** Horizon profile, obstruction geometries
- **Output:** Shading loss factor per timestamp

#### FR-13: Bifacial Panel Support (Future Enhancement)
- **Priority:** Low
- **Description:** Model rear-side irradiance for bifacial panels
- **Complexity:** Requires ground-reflected and sky-view modeling

---

## 4. Non-Functional Requirements

### NFR-1: Performance
- Instantaneous calculation: < 10ms per data point
- Annual simulation (5-min intervals): < 30 seconds for 1 year
- Support for vectorized calculations using NumPy
- Efficient memory usage for large time series

### NFR-2: Accuracy
- Solar position: ±0.01° error (SPA algorithm standard)
- Clear-sky irradiance: Within 5% of measured data under clear conditions
- Overall power estimation: Within 10-15% of actual production (typical for simulation)
- Temperature modeling: ±3°C cell temperature accuracy

### NFR-3: Reliability
- 100% unit test coverage for core calculations
- Integration tests with real-world data validation
- Graceful error handling and informative exceptions
- Input validation with clear error messages

### NFR-4: Usability
- Clear, comprehensive documentation with examples
- Type hints for all public APIs (PEP 484)
- Jupyter notebook tutorials
- Quickstart guide for common use cases
- API reference documentation (Sphinx)

### NFR-5: Compatibility
- Python 3.9+ support
- Cross-platform (Windows, macOS, Linux)
- Minimal dependencies (NumPy, Pandas, SciPy, Requests)
- Optional dependencies for advanced features (Matplotlib for plotting)

### NFR-6: Maintainability
- Modular architecture with clear separation of concerns
- PEP 8 compliant code style
- Continuous Integration (GitHub Actions)
- Semantic versioning (SemVer)

### NFR-7: Licensing
- Open-source license (MIT or BSD-3)
- Clear attribution to underlying models (pvlib, etc.)
- No proprietary dependencies

---

## 5. API Design

### 5.1 High-Level API (Simple Interface)

```python
from pvsolarsim import PVSystem, Location, calculate_power

# Quick calculation
location = Location(latitude=49.8, longitude=15.5, altitude=300)
system = PVSystem(
    panel_area=20.0,  # m²
    panel_efficiency=0.20,  # 20%
    tilt=35,  # degrees
    azimuth=180,  # South-facing
    temp_coefficient=-0.004  # %/°C
)

# Instantaneous power at specific time
from datetime import datetime
timestamp = datetime(2025, 6, 21, 12, 0, tzinfo='UTC')
power = calculate_power(
    location=location,
    system=system,
    timestamp=timestamp,
    ambient_temp=25,  # °C
    wind_speed=3,  # m/s
    cloud_cover=20  # %
)
print(f"Estimated power: {power} W")

# Annual simulation
from pvsolarsim import simulate_annual

results = simulate_annual(
    location=location,
    system=system,
    year=2025,
    interval='5min',
    weather_source='openweathermap',
    api_key='YOUR_API_KEY'
)

print(f"Annual production: {results.total_energy_kwh} kWh")
print(f"Capacity factor: {results.capacity_factor * 100:.2f}%")
results.plot_monthly()
```

### 5.2 Low-Level API (Advanced Control)

```python
from pvsolarsim.solar import SolarPosition
from pvsolarsim.atmosphere import ClearSkyModel, CloudCoverModel
from pvsolarsim.irradiance import POACalculator
from pvsolarsim.temperature import CellTemperatureModel

# Fine-grained control
solar_pos = SolarPosition(lat=49.8, lon=15.5, alt=300)
sun = solar_pos.calculate(timestamp)

clear_sky = ClearSkyModel(model='simplified_solis')
irrad_clear = clear_sky.calculate(
    apparent_elevation=sun.elevation,
    aod700=0.1,
    precipitable_water=1.5,
    pressure=101325
)

cloud_model = CloudCoverModel()
irrad_actual = cloud_model.apply(irrad_clear, cloud_cover=20)

poa_calc = POACalculator(tilt=35, azimuth=180, model='perez')
poa = poa_calc.calculate(
    dni=irrad_actual.dni,
    dhi=irrad_actual.dhi,
    ghi=irrad_actual.ghi,
    solar_zenith=sun.zenith,
    solar_azimuth=sun.azimuth
)

temp_model = CellTemperatureModel(model='sapm')
cell_temp = temp_model.calculate(
    poa_irradiance=poa.global_poa,
    ambient_temp=25,
    wind_speed=3
)
```

### 5.3 Data Classes

```python
@dataclass
class Location:
    latitude: float
    longitude: float
    altitude: float = 0
    timezone: str = 'UTC'

@dataclass
class PVSystem:
    panel_area: float  # m²
    panel_efficiency: float  # 0-1
    tilt: float  # degrees
    azimuth: float  # degrees
    temp_coefficient: float  # %/°C
    noct: float = 45  # °C
    reference_temp: float = 25  # °C
    iam_model: str = 'ashrae'
    diffuse_model: str = 'perez'

@dataclass
class IrradianceComponents:
    ghi: float  # W/m²
    dni: float  # W/m²
    dhi: float  # W/m²

@dataclass
class SimulationResult:
    time_series: pd.DataFrame
    total_energy_kwh: float
    capacity_factor: float
    peak_power_w: float
    average_power_w: float
```

---

## 6. Technical Architecture

### 6.1 Module Structure

```
pvsolarsim/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── location.py          # Location and coordinate handling
│   ├── system.py            # PVSystem configuration
│   └── constants.py         # Physical constants
├── solar/
│   ├── __init__.py
│   ├── position.py          # Solar position calculations (SPA)
│   └── geometry.py          # Solar geometry utilities
├── atmosphere/
│   ├── __init__.py
│   ├── clearsky.py          # Clear-sky models (Ineichen, Solis, Bird)
│   ├── airmass.py           # Air mass calculations
│   ├── cloudcover.py        # Cloud cover effects
│   └── turbidity.py         # Linke turbidity lookup
├── irradiance/
│   ├── __init__.py
│   ├── poa.py               # Plane-of-array calculations
│   ├── transposition.py     # Diffuse transposition models
│   ├── iam.py               # Incidence angle modifiers
│   └── decomposition.py     # GHI to DNI/DHI
├── temperature/
│   ├── __init__.py
│   └── models.py            # Cell temperature models (Faiman, SAPM, King)
├── weather/
│   ├── __init__.py
│   ├── api_clients.py       # API integrations (OpenWeather, PVGIS)
│   ├── readers.py           # File readers (CSV, JSON, TMY)
│   └── cache.py             # Data caching
├── simulation/
│   ├── __init__.py
│   ├── engine.py            # Main simulation engine
│   ├── timeseries.py        # Time series generation
│   └── statistics.py        # Statistical analysis
├── utils/
│   ├── __init__.py
│   ├── validators.py        # Input validation
│   ├── converters.py        # Unit conversions
│   └── exceptions.py        # Custom exceptions
└── plotting/
    ├── __init__.py
    └── visualizations.py    # Plotting utilities
```

### 6.2 Dependencies

**Core Dependencies:**
- `numpy >= 1.24.0` - Numerical computations
- `pandas >= 2.0.0` - Time series handling
- `scipy >= 1.10.0` - Scientific computations
- `requests >= 2.31.0` - HTTP requests for weather APIs
- `python-dateutil >= 2.8.0` - Timezone handling

**Optional Dependencies:**
- `matplotlib >= 3.7.0` - Plotting
- `pvlib >= 0.10.0` - Reference implementation validation (optional)
- `pytest >= 7.4.0` - Testing (dev)
- `sphinx >= 7.0.0` - Documentation (dev)

---

## 7. Testing Strategy

### 7.1 Unit Tests
- All calculation functions with known inputs/outputs
- Edge cases (sunrise, sunset, midnight, polar regions)
- Invalid input handling

### 7.2 Integration Tests
- Full workflow from location to power output
- Weather API integration
- Annual simulation accuracy

### 7.3 Validation
- Comparison with pvlib-python results
- Validation against measured data from real installations
- Benchmark against NREL SAM outputs

### 7.4 Performance Tests
- Execution time benchmarks
- Memory profiling
- Scalability tests (multi-year simulations)

---

## 8. Documentation Requirements

### 8.1 User Documentation
- README.md with installation and quick start
- API reference (auto-generated from docstrings)
- Tutorial notebooks:
  - Basic instantaneous calculation
  - Annual simulation workflow
  - Weather data integration
  - Advanced configuration
- FAQ and troubleshooting guide

### 8.2 Developer Documentation
- Architecture overview
- Contributing guidelines
- Code style guide
- Release process

### 8.3 Scientific Documentation
- Mathematical models explanation
- References to academic papers
- Model validation results
- Accuracy and limitations

---

## 9. Deployment and Distribution

### 9.1 PyPI Package
- Package name: `pvsolarsim`
- Versioning: SemVer (e.g., 1.0.0)
- Classifiers:
  - Development Status :: 4 - Beta
  - Intended Audience :: Science/Research
  - Topic :: Scientific/Engineering
  - License :: OSI Approved :: MIT License
  - Programming Language :: Python :: 3.9+

### 9.2 GitHub Repository
- Public repository: github.com/jenicek001/pvsolarsim
- Branch strategy: main (stable), develop (active development)
- GitHub Actions CI/CD
- Issue templates and PR guidelines

### 9.3 Conda Package (Future)
- Conda-forge distribution for scientific users

---

## 10. Success Criteria

### 10.1 Functional Success
- ✅ Accurate instantaneous power calculation (validated against pvlib)
- ✅ Annual simulation runs without errors
- ✅ Weather API integration works reliably
- ✅ All core features implemented and tested

### 10.2 Quality Success
- ✅ > 90% test coverage
- ✅ Documentation completeness score > 95%
- ✅ Zero critical bugs in release
- ✅ Performance benchmarks met

### 10.3 Adoption Success
- 🎯 Published to PyPI within 3 months
- 🎯 10+ GitHub stars in first month
- 🎯 Positive feedback from initial users
- 🎯 Integration in at least one third-party project

---

## 11. Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Accuracy issues vs. real data | Medium | High | Extensive validation, multiple model options |
| Weather API rate limits | High | Medium | Caching, multiple provider support |
| Performance bottlenecks | Low | Medium | Profiling, vectorization, optional numba |
| Complex API for users | Medium | Medium | High-level wrapper functions, examples |
| Dependency conflicts | Low | Low | Minimal dependencies, version pinning |

---

## 12. Timeline and Milestones

### Phase 1: Core Engine (Weeks 1-4)
- Solar position calculations
- Atmospheric models
- POA irradiance calculations
- Basic instantaneous power calculation

### Phase 2: Simulation Framework (Weeks 5-7)
- Time series generation
- Temperature modeling
- Annual simulation engine
- Basic weather data integration

### Phase 3: Weather Integration (Weeks 8-9)
- OpenWeatherMap API client
- PVGIS data reader
- CSV/JSON file support
- Data caching

### Phase 4: Testing and Validation (Weeks 10-11)
- Comprehensive unit tests
- Integration tests
- Validation against reference data
- Performance optimization

### Phase 5: Documentation and Release (Weeks 12-13)
- Complete API documentation
- Tutorial notebooks
- PyPI packaging
- Initial release

---

## 13. Future Enhancements (Post v1.0)

1. **Shade Analysis Module** - 3D obstruction modeling
2. **Bifacial Panel Support** - Rear-side irradiance modeling
3. **Soiling and Degradation Models** - Temporal performance reduction
4. **Battery Storage Integration** - Energy storage simulation
5. **Economic Analysis** - LCOE, ROI calculations
6. **Machine Learning Integration** - Forecast improvements
7. **Real-time Monitoring** - Live data stream processing
8. **Web API** - RESTful service deployment

---

## Appendices

### A. References
- Holmgren, W. F., et al. (2018). "pvlib python: a python package for modeling solar energy systems." JOSS.
- Ineichen, P., & Perez, R. (2002). "A new airmass independent formulation for the Linke turbidity coefficient."
- Bird, R. E., & Hulstrom, R. L. (1981). "Simplified clear sky model for direct and diffuse insolation."
- OpenWeatherMap API Documentation: https://openweathermap.org/api

### B. Glossary
- **GHI**: Global Horizontal Irradiance
- **DNI**: Direct Normal Irradiance
- **DHI**: Diffuse Horizontal Irradiance
- **POA**: Plane of Array
- **AOI**: Angle of Incidence
- **IAM**: Incidence Angle Modifier
- **STC**: Standard Test Conditions (25°C, 1000 W/m²)
- **NOCT**: Nominal Operating Cell Temperature
- **AOD**: Aerosol Optical Depth
- **TMY**: Typical Meteorological Year

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-23 | GitHub Copilot | Initial draft |

