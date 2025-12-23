# PVSolarSim Python Library - Project Planning

**Project Name:** PVSolarSim  
**Repository:** github.com/jenicek001/pvsolarsim  
**Type:** Public PyPI Python Package  
**Status:** Planning Phase  
**Start Date:** December 23, 2025  
**Target Release:** v1.0.0 by March 2026

---

## Project Overview

PVSolarSim is a comprehensive Python library for calculating photovoltaic energy production. It provides accurate physics-based modeling of solar irradiance, atmospheric effects, and PV system performance.

### Key Objectives
1. Create production-ready Python package for PV power calculation
2. Achieve PyPI publication with comprehensive documentation
3. Validate accuracy against pvlib-python and real-world data
4. Provide simple API for common use cases and advanced API for researchers
5. Enable annual energy production simulations with weather integration

---

## Development Phases

### Phase 1: Foundation & Core Engine (Weeks 1-4)

#### **Week 1: Project Setup & Architecture**

**Goals:**
- Initialize repository structure
- Set up development environment
- Establish coding standards and CI/CD pipeline
- Create basic package structure

**Tasks:**
- [ ] Create GitHub repository (public)
- [ ] Initialize Python package structure
  ```
  pvsolarsim/
  ├── src/pvsolarsim/
  ├── tests/
  ├── docs/
  ├── examples/
  ├── setup.py
  ├── pyproject.toml
  ├── README.md
  └── LICENSE (MIT)
  ```
- [ ] Set up virtual environment with Poetry or pip-tools
- [ ] Configure pytest, black, ruff, mypy
- [ ] Create GitHub Actions workflows:
  - [ ] CI: Run tests on every push/PR
  - [ ] CD: Publish to PyPI on release tag
  - [ ] Code quality checks (linting, type checking)
- [ ] Initialize documentation with Sphinx
- [ ] Write CONTRIBUTING.md guidelines

**Deliverables:**
- ✅ Functional repository with CI/CD
- ✅ Basic package installable via `pip install -e .`
- ✅ Testing framework operational

**Dependencies:** None

---

#### **Week 2: Solar Position Calculations**

**Goals:**
- Implement accurate solar position algorithms
- Create Location class and solar geometry utilities

**Tasks:**
- [ ] Implement `Location` dataclass
  - Latitude, longitude, altitude, timezone
  - Validation (lat: -90 to 90, lon: -180 to 180)
- [ ] Implement Solar Position Algorithm (SPA)
  - Option 1: Use pvlib.solarposition as dependency
  - Option 2: Implement from NREL SPA C code (pure Python)
  - Recommendation: Start with pvlib, make optional/pluggable
- [ ] Create `SolarPosition` class
  - Methods: `calculate(timestamp)` → (azimuth, zenith, elevation, etc.)
  - Support for single timestamp and time series (vectorized)
- [ ] Implement solar geometry utilities
  - Hour angle calculation
  - Declination
  - Equation of time
  - Sunrise/sunset times
- [ ] Write comprehensive unit tests
  - Test against known values (NREL SPA test data)
  - Edge cases: polar regions, equator, solstices, equinoxes

**Deliverables:**
- ✅ `pvsolarsim.solar.position` module
- ✅ Test coverage > 95%
- ✅ Accuracy: < 0.01° error vs. NREL SPA

**Dependencies:**
- NumPy, Pandas, python-dateutil

**Code Example:**
```python
from pvsolarsim import Location
from pvsolarsim.solar import SolarPosition
from datetime import datetime

loc = Location(latitude=49.8, longitude=15.5, altitude=300)
solar_pos = SolarPosition(loc)

timestamp = datetime(2025, 6, 21, 12, 0, tzinfo='UTC')
sun = solar_pos.calculate(timestamp)

print(f"Azimuth: {sun.azimuth:.2f}°")
print(f"Elevation: {sun.elevation:.2f}°")
```

---

#### **Week 3: Atmospheric Modeling**

**Goals:**
- Implement clear-sky irradiance models
- Create air mass calculations
- Support Linke turbidity and AOD

**Tasks:**
- [ ] Implement air mass calculations
  - Relative air mass (Kasten-Young formula)
  - Absolute air mass (pressure correction)
- [ ] Implement Simplified Solis clear-sky model
  - Inputs: apparent elevation, AOD, precipitable water, pressure
  - Outputs: GHI, DNI, DHI
- [ ] Implement Ineichen clear-sky model
  - Linke turbidity support
  - Altitude correction
- [ ] Implement Bird clear-sky model (optional, for validation)
- [ ] Create Linke turbidity lookup table
  - Monthly climatology data
  - Interpolation by location
- [ ] Implement `ClearSkyModel` base class with strategy pattern
  - Subclasses: `SimplifiedSolis`, `Ineichen`, `Bird`
  - Unified interface
- [ ] Write unit tests
  - Compare against pvlib results
  - Test different turbidity values
  - Validate extreme solar angles

**Deliverables:**
- ✅ `pvsolarsim.atmosphere.clearsky` module
- ✅ Multiple model options
- ✅ Test coverage > 90%

**Dependencies:**
- SciPy (for interpolation)

**Code Example:**
```python
from pvsolarsim.atmosphere import ClearSkyModel

clear_sky = ClearSkyModel(model='simplified_solis')
irradiance = clear_sky.calculate(
    apparent_elevation=45.0,
    aod700=0.1,
    precipitable_water=1.5,
    pressure=101325
)

print(f"GHI: {irradiance.ghi} W/m²")
print(f"DNI: {irradiance.dni} W/m²")
print(f"DHI: {irradiance.dhi} W/m²")
```

---

#### **Week 4: Plane-of-Array (POA) Irradiance**

**Goals:**
- Calculate irradiance on tilted surfaces
- Implement multiple diffuse transposition models
- Support incident angle modifiers

**Tasks:**
- [ ] Implement `PVSystem` dataclass
  - Panel area, efficiency, tilt, azimuth
  - Temperature coefficient, NOCT
  - IAM and diffuse model preferences
- [ ] Implement angle of incidence (AOI) calculation
  - Angle between sun vector and panel normal
- [ ] Implement beam irradiance projection
  - `beam_component = DNI * cos(AOI)`
- [ ] Implement diffuse transposition models
  - [ ] Isotropic (simplest)
  - [ ] Hay-Davies (circumsolar + isotropic)
  - [ ] Perez (anisotropic, industry standard)
  - [ ] Klucher (horizon brightening)
  - [ ] Reindl (GHI-based)
- [ ] Implement ground-reflected irradiance
  - `ground_reflected = GHI * albedo * (1 - cos(tilt)) / 2`
- [ ] Implement Incidence Angle Modifiers (IAM)
  - [ ] ASHRAE model
  - [ ] Physical (Fresnel) model
  - [ ] Martin-Ruiz model
  - [ ] SAPM model (optional)
- [ ] Create `POACalculator` class
  - Method: `calculate(dni, dhi, ghi, solar_pos, system)` → POA components
- [ ] Write unit tests
  - Validate against pvlib
  - Test different tilt/azimuth combinations
  - Edge cases: vertical panels, horizontal panels

**Deliverables:**
- ✅ `pvsolarsim.irradiance.poa` module
- ✅ `pvsolarsim.irradiance.iam` module
- ✅ Support for 5+ diffuse models
- ✅ Test coverage > 90%

**Code Example:**
```python
from pvsolarsim import PVSystem
from pvsolarsim.irradiance import POACalculator

system = PVSystem(
    panel_area=20.0,
    panel_efficiency=0.20,
    tilt=35,
    azimuth=180
)

poa_calc = POACalculator(system, model='perez')
poa = poa_calc.calculate(
    dni=irradiance.dni,
    dhi=irradiance.dhi,
    ghi=irradiance.ghi,
    solar_zenith=sun.zenith,
    solar_azimuth=sun.azimuth
)

print(f"POA Global: {poa.global_poa} W/m²")
print(f"POA Direct: {poa.direct} W/m²")
print(f"POA Diffuse: {poa.diffuse} W/m²")
```

---

### Phase 2: Simulation Framework (Weeks 5-7)

#### **Week 5: Temperature Modeling**

**Goals:**
- Implement cell/module temperature models
- Calculate temperature-dependent efficiency

**Tasks:**
- [ ] Implement temperature models
  - [ ] Faiman model (radiative + convective)
  - [ ] SAPM (Sandia Array Performance Model)
  - [ ] King model
  - [ ] Generic linear model
- [ ] Create `CellTemperatureModel` base class
- [ ] Implement temperature correction factor
  - `P_corrected = P_stc * [1 + temp_coeff * (T_cell - T_ref)]`
- [ ] Account for wind speed effects
- [ ] Write unit tests
  - Validate against literature values
  - Test extreme temperatures (-20°C to 60°C)

**Deliverables:**
- ✅ `pvsolarsim.temperature.models` module
- ✅ Multiple model options
- ✅ Test coverage > 85%

**Code Example:**
```python
from pvsolarsim.temperature import CellTemperatureModel

temp_model = CellTemperatureModel(model='sapm')
cell_temp = temp_model.calculate(
    poa_irradiance=800,  # W/m²
    ambient_temp=25,     # °C
    wind_speed=3         # m/s
)

temp_factor = 1 + system.temp_coefficient * (cell_temp - 25)
print(f"Temperature correction: {temp_factor:.4f}")
```

---

#### **Week 6: Instantaneous Power Calculation**

**Goals:**
- Integrate all components into power calculation
- Create high-level API for simple use cases

**Tasks:**
- [ ] Implement `calculate_power()` function
  - Inputs: location, system, timestamp, weather conditions
  - Pipeline:
    1. Solar position
    2. Clear-sky irradiance (or use provided GHI/DNI/DHI)
    3. Cloud cover adjustment
    4. POA calculation
    5. Temperature modeling
    6. IAM application
    7. Power output
  - Output: Power (W), intermediate values (optional)
- [ ] Create `PowerCalculator` class (stateful, optimized for repeated calls)
- [ ] Implement cloud cover model
  - Campbell-Norman formula
  - Custom attenuation factors
- [ ] Add soiling/degradation factors
- [ ] Write integration tests
  - End-to-end validation
  - Compare with pvlib ModelChain
- [ ] Write user-friendly examples

**Deliverables:**
- ✅ `pvsolarsim.calculate_power()` function
- ✅ `pvsolarsim.PowerCalculator` class
- ✅ Integration tests
- ✅ Example notebooks

**Code Example:**
```python
from pvsolarsim import Location, PVSystem, calculate_power
from datetime import datetime

location = Location(latitude=49.8, longitude=15.5, altitude=300)
system = PVSystem(
    panel_area=20.0,
    panel_efficiency=0.20,
    tilt=35,
    azimuth=180,
    temp_coefficient=-0.004
)

power = calculate_power(
    location=location,
    system=system,
    timestamp=datetime(2025, 6, 21, 12, 0),
    ambient_temp=25,
    wind_speed=3,
    cloud_cover=20
)

print(f"Instantaneous power: {power.power_w:.2f} W")
print(f"POA irradiance: {power.poa_irradiance:.2f} W/m²")
```

---

#### **Week 7: Time Series & Annual Simulation**

**Goals:**
- Generate time series for extended periods
- Create simulation engine for annual runs

**Tasks:**
- [ ] Implement time series generation
  - Date range with configurable intervals (5min, 15min, hourly)
  - Timezone-aware
  - Daylight filtering option
- [ ] Create `SimulationEngine` class
  - Batch processing of timestamps
  - Vectorization for performance (NumPy arrays)
  - Progress callback support
- [ ] Implement `simulate_annual()` function
  - High-level API for annual simulations
  - Returns `SimulationResult` dataclass
- [ ] Create `SimulationResult` class
  - Time series DataFrame
  - Summary statistics (total energy, capacity factor, etc.)
  - Plotting methods (`.plot_monthly()`, `.plot_daily()`)
- [ ] Implement statistical analysis
  - Daily, monthly, annual aggregations
  - Percentiles (P50, P90, P99)
  - Performance metrics
- [ ] Optimize performance
  - Profile code for bottlenecks
  - Use NumPy vectorization
  - Consider Numba JIT for hot loops (optional)
- [ ] Write performance benchmarks

**Deliverables:**
- ✅ `pvsolarsim.simulation.engine` module
- ✅ `simulate_annual()` function
- ✅ Performance: < 30s for annual simulation (5min intervals)
- ✅ Benchmark tests

**Code Example:**
```python
from pvsolarsim import simulate_annual

results = simulate_annual(
    location=location,
    system=system,
    year=2025,
    interval='5min',
    weather_source='clear_sky',  # Start with theoretical
    turbidity='medium'
)

print(f"Annual energy: {results.total_energy_kwh:.2f} kWh")
print(f"Capacity factor: {results.capacity_factor * 100:.2f}%")
print(f"Peak power: {results.peak_power_w:.2f} W")

# Plot results
results.plot_monthly()
results.export_csv('results.csv')
```

---

### Phase 3: Weather Integration (Weeks 8-9)

#### **Week 8: Weather Data APIs**

**Goals:**
- Integrate OpenWeatherMap Solar API
- Support PVGIS TMY data
- Implement data caching

**Tasks:**
- [ ] Create `WeatherDataSource` abstract base class
- [ ] Implement OpenWeatherMap client
  - [ ] API authentication
  - [ ] Fetch historical weather data
  - [ ] Parse GHI, DNI, DHI, temperature, wind, cloud cover
  - [ ] Rate limiting handling
  - [ ] Error handling (network, API errors)
- [ ] Implement PVGIS client
  - [ ] TMY data download
  - [ ] Hourly radiation data
  - [ ] Parse PVGIS CSV format
- [ ] Implement file readers
  - [ ] CSV reader (generic format with column mapping)
  - [ ] JSON reader
  - [ ] EPW reader (EnergyPlus Weather format, optional)
- [ ] Create caching layer
  - [ ] Cache weather data to local SQLite/pickle
  - [ ] TTL-based expiration
  - [ ] Cache invalidation
- [ ] Write integration tests with mock API responses
- [ ] Create example notebooks with real weather data

**Deliverables:**
- ✅ `pvsolarsim.weather.api_clients` module
- ✅ `pvsolarsim.weather.readers` module
- ✅ OpenWeatherMap integration working
- ✅ Caching functional

**Code Example:**
```python
from pvsolarsim import simulate_annual
from pvsolarsim.weather import OpenWeatherMapClient

# Automatic weather integration
results = simulate_annual(
    location=location,
    system=system,
    year=2024,
    interval='5min',
    weather_source='openweathermap',
    api_key='YOUR_API_KEY'
)

# Or manual weather data provision
from pvsolarsim.weather import CSVWeatherReader

weather_data = CSVWeatherReader('weather.csv', column_mapping={
    'timestamp': 'datetime',
    'temperature': 'temp_c',
    'ghi': 'irradiance_ghi'
})

results = simulate_annual(
    location=location,
    system=system,
    weather_data=weather_data
)
```

---

#### **Week 9: Cloud Cover & Advanced Weather**

**Goals:**
- Refine cloud cover models
- Implement weather interpolation
- Handle missing data

**Tasks:**
- [ ] Improve cloud cover to irradiance conversion
  - Campbell-Norman model
  - Clearness index approach
  - Validate against measured data
- [ ] Implement data interpolation
  - Linear interpolation for missing timestamps
  - Spline interpolation (optional)
  - Forward/backward fill
- [ ] Add data quality checks
  - Flag suspicious values (e.g., nighttime GHI > 0)
  - Identify and fill gaps
- [ ] Create weather data validator
  - Check value ranges (GHI 0-1500, temp -50 to 60, etc.)
  - Consistency checks (GHI >= DHI + DNI*cos(zenith))
- [ ] Write comprehensive weather integration tests
- [ ] Document weather data requirements and formats

**Deliverables:**
- ✅ Robust weather data handling
- ✅ Data validation and cleaning
- ✅ Documentation for custom weather data

---

### Phase 4: Testing, Validation & Documentation (Weeks 10-11)

#### **Week 10: Comprehensive Testing & Validation**

**Goals:**
- Achieve >90% test coverage
- Validate against pvlib and real-world data
- Performance optimization

**Tasks:**
- [ ] Write additional unit tests for edge cases
- [ ] Integration tests for full workflows
- [ ] Validation tests
  - [ ] Compare with pvlib-python (10+ test cases)
  - [ ] Validate against NREL SAM (3+ cases)
  - [ ] Compare with real installation data (if available)
  - [ ] Document accuracy (RMSE, MAE, MAPE)
- [ ] Performance optimization
  - [ ] Profile code with cProfile
  - [ ] Optimize hot paths
  - [ ] Consider Numba for critical loops
  - [ ] Ensure vectorization is used
- [ ] Stress testing
  - [ ] Multi-year simulations (5+ years)
  - [ ] High-resolution intervals (1-minute)
  - [ ] Memory leak testing
- [ ] Create validation report
  - Accuracy metrics
  - Performance benchmarks
  - Comparison table with other tools

**Deliverables:**
- ✅ Test coverage > 90%
- ✅ Validation report published
- ✅ Performance targets met

**Validation Metrics:**
| Metric | Target | Actual |
|--------|--------|--------|
| Solar position accuracy | < 0.01° | TBD |
| Clear-sky GHI error vs. pvlib | < 2% | TBD |
| Annual energy error vs. real data | < 15% | TBD |
| Execution time (1 year, 5min) | < 30s | TBD |

---

#### **Week 11: Documentation & Examples**

**Goals:**
- Complete API documentation
- Write tutorials and guides
- Prepare for PyPI release

**Tasks:**
- [ ] Complete docstrings for all public APIs
  - NumPy-style docstrings
  - Include examples in docstrings
  - Type hints everywhere
- [ ] Build Sphinx documentation
  - [ ] API reference (auto-generated)
  - [ ] User guide
    - Installation
    - Quick start
    - Core concepts
    - Advanced usage
  - [ ] Tutorials (Jupyter notebooks)
    - Basic instantaneous calculation
    - Annual simulation with clear-sky
    - Annual simulation with real weather
    - Multi-location comparison
    - Custom panel parameters
  - [ ] FAQ and troubleshooting
  - [ ] Mathematical background (models explained)
- [ ] Update README.md
  - Installation instructions
  - Quick example
  - Features list
  - Links to documentation
  - Badges (CI status, coverage, PyPI version)
- [ ] Write CONTRIBUTING.md
  - Development setup
  - Code style
  - Testing guidelines
  - PR process
- [ ] Create CHANGELOG.md
- [ ] Prepare for PyPI release
  - [ ] Finalize setup.py / pyproject.toml
  - [ ] Write long_description from README
  - [ ] Set classifiers
  - [ ] Test package build (`python -m build`)
  - [ ] Test installation in clean environment

**Deliverables:**
- ✅ Complete documentation hosted (Read the Docs)
- ✅ 5+ tutorial notebooks
- ✅ README with clear examples
- ✅ Package ready for PyPI

---

### Phase 5: PyPI Release & Initial Support (Weeks 12-13)

#### **Week 12: Alpha/Beta Release**

**Goals:**
- Release v0.9.0 (beta) to PyPI
- Gather feedback from early users
- Fix critical bugs

**Tasks:**
- [ ] Create release checklist
  - [ ] All tests passing
  - [ ] Documentation complete
  - [ ] Version bumped to 0.9.0
  - [ ] CHANGELOG updated
- [ ] Build and test package
  ```bash
  python -m build
  twine check dist/*
  ```
- [ ] Upload to Test PyPI
  ```bash
  twine upload --repository testpypi dist/*
  ```
- [ ] Test installation from Test PyPI
- [ ] Upload to PyPI
  ```bash
  twine upload dist/*
  ```
- [ ] Create GitHub release (tag v0.9.0)
- [ ] Announce beta release
  - Reddit (r/solar, r/Python)
  - Twitter/X
  - LinkedIn
  - Discord/Slack communities
- [ ] Set up issue templates on GitHub
- [ ] Monitor for bug reports
- [ ] Provide user support

**Deliverables:**
- ✅ Package on PyPI (`pip install pvsolarsim`)
- ✅ GitHub release with release notes
- ✅ User feedback collected

---

#### **Week 13: v1.0.0 Release**

**Goals:**
- Address beta feedback
- Release stable v1.0.0
- Establish maintenance plan

**Tasks:**
- [ ] Fix bugs reported during beta
- [ ] Improve documentation based on user questions
- [ ] Final validation and testing
- [ ] Version bump to 1.0.0
- [ ] Create comprehensive release notes
- [ ] Publish v1.0.0 to PyPI
- [ ] Update documentation to mark as stable
- [ ] Write blog post / announcement
- [ ] Submit to:
  - Python Weekly newsletter
  - Awesome Python lists
  - PV Performance Modeling Collaborative
- [ ] Plan roadmap for v1.1 and beyond

**Deliverables:**
- ✅ Stable v1.0.0 release
- ✅ Public announcement and marketing
- ✅ Roadmap for future development

---

## Post-Release Maintenance

### Ongoing Activities
- **Bug Fixes:** Address issues reported by users
- **Documentation Updates:** Improve based on feedback
- **Dependency Updates:** Keep dependencies current
- **Security Patches:** Monitor and fix vulnerabilities

### Feature Roadmap (v1.1+)
- **v1.1:** Shade analysis, bifacial panels
- **v1.2:** Economic analysis (LCOE, ROI)
- **v1.3:** Battery storage simulation
- **v2.0:** Machine learning integration, advanced forecasting

---

## Risk Management

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Accuracy issues vs. pvlib | Medium | High | Continuous validation, multiple test cases |
| Performance bottlenecks | Low | Medium | Early profiling, optimization |
| Weather API changes/limits | Medium | Medium | Support multiple providers, caching |
| Dependency conflicts | Low | Low | Pin versions, test in CI |
| Low adoption | Medium | Medium | Good docs, examples, marketing |

---

## Success Metrics

### Technical Metrics
- [x] All functional requirements implemented
- [ ] >90% test coverage achieved
- [ ] Documentation score >95% (interrogate)
- [ ] Zero critical bugs in v1.0.0
- [ ] Performance benchmarks met

### Adoption Metrics
- [ ] Published to PyPI
- [ ] 50+ downloads in first week
- [ ] 10+ GitHub stars in first month
- [ ] At least 3 external contributors by month 3
- [ ] Featured in at least one blog/newsletter

### Quality Metrics
- [ ] Positive user feedback (>80% satisfaction)
- [ ] < 5% error rate in production use
- [ ] Active issue resolution (< 7 day response time)

---

## Resources

### Team
- **Lead Developer:** AI-assisted development (GitHub Copilot)
- **Code Review:** Automated (CI/CD) + Human review
- **Documentation:** AI-assisted writing + Technical writer
- **Testing:** Automated testing + Manual validation

### Tools
- **IDE:** VS Code with Python extensions
- **Version Control:** Git + GitHub
- **CI/CD:** GitHub Actions
- **Testing:** pytest, pytest-cov
- **Docs:** Sphinx, Read the Docs
- **Package Build:** build, twine
- **Code Quality:** black, ruff, mypy

### External Dependencies
- pvlib-python (reference, optional dependency)
- NumPy, Pandas, SciPy
- Requests (HTTP client)
- python-dateutil (timezone handling)

---

## Communication Plan

### Internal Updates
- Weekly progress reviews
- Daily standup summaries (async)
- GitHub Projects for task tracking

### External Communication
- Monthly blog posts during development
- Beta release announcement
- v1.0 press release
- Active response on GitHub issues

---

## Appendix: Development Commands

### Setup
```bash
git clone https://github.com/jenicek001/pvsolarsim.git
cd pvsolarsim
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Testing
```bash
pytest                          # Run all tests
pytest --cov=pvsolarsim         # With coverage
pytest -v -s                    # Verbose with output
pytest tests/test_solar.py      # Specific test file
```

### Code Quality
```bash
black src/                      # Format code
ruff check src/                 # Lint
mypy src/                       # Type check
```

### Documentation
```bash
cd docs
make html                       # Build HTML docs
make clean && make html         # Clean build
```

### Build Package
```bash
python -m build                 # Build wheel and sdist
twine check dist/*              # Validate
```

### Release
```bash
git tag v1.0.0
git push origin v1.0.0
twine upload dist/*
```

---

**Last Updated:** December 23, 2025  
**Next Review:** Weekly during development
