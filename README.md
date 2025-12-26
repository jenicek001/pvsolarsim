# PVSolarSim

**Python library for photovoltaic (PV) solar energy simulation**

[![PyPI version](https://badge.fury.io/py/pvsolarsim.svg)](https://badge.fury.io/py/pvsolarsim)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🌞 Overview

PVSolarSim is a comprehensive Python library for simulating photovoltaic solar energy production. 

### Currently Implemented (v0.1.0)

- ✅ **Solar position** calculations using NREL's SPA algorithm (via pvlib)
- ✅ **Atmospheric modeling** with clear-sky irradiance (Ineichen and Simplified Solis models)
- ✅ **Cloud cover modeling** with 3 validated models (Campbell-Norman, Simple Linear, Kasten-Czeplak)
- ✅ **Plane-of-array (POA) irradiance** with multiple diffuse transposition models (Isotropic, Perez, Hay-Davies)
- ✅ **Incidence angle modifiers (IAM)** for reflection losses (ASHRAE, Physical, Martin-Ruiz)
- ✅ **Cell temperature modeling** with 4 validated models (Faiman, SAPM, PVsyst, Generic Linear)
- ✅ **Instantaneous power calculation** integrating all PV modeling components
- ✅ **Annual energy simulation** with time series and statistical analysis
- ✅ **Location and PV system** data models with validation
- ✅ **High accuracy**: Solar position <0.01° error, all models validated against pvlib
- ✅ **Type-safe**: Full type hints with mypy validation
- ✅ **Well-tested**: 98.52% code coverage with 199 comprehensive tests

### Coming Soon (Roadmap)

- 🔄 **Weather data integration** (OpenWeatherMap, PVGIS, CSV) - Weeks 8-9
- 🔄 **Documentation with Sphinx** - Week 11

### Key Features

- ✅ **High Accuracy**: Solar position accuracy <0.01° using NREL SPA algorithm
- ✅ **Multiple Clear-Sky Models**: Ineichen (Linke turbidity), Simplified Solis (AOD)
- ✅ **Cloud Cover Models**: Campbell-Norman, Simple Linear, Kasten-Czeplak
- ✅ **Multiple Diffuse Models**: Isotropic, Perez (industry standard), Hay-Davies
- ✅ **Multiple Diffuse Models**: Isotropic, Perez (industry standard), Hay-Davies
- ✅ **Temperature Models**: Faiman, SAPM, PVsyst, Generic Linear (all validated against pvlib)
- ✅ **IAM Support**: ASHRAE, Physical (Fresnel), Martin-Ruiz models
- ✅ **Vectorized Operations**: NumPy-based calculations for performance
- ✅ **Type-Safe**: Full type hints and runtime validation
- ✅ **Well-Tested**: >97% code coverage, validated against pvlib-python
- ✅ **Easy to Use**: Clean API with comprehensive documentation

## 🚀 Installation

```bash
pip install pvsolarsim
```

For development:
```bash
git clone https://github.com/jenicek001/pvsolarsim.git
cd pvsolarsim
pip install -e ".[dev]"
```

## 📖 Quick Start

### Solar Position Calculation

```python
from pvsolarsim.solar import calculate_solar_position
from datetime import datetime
import pytz

# Calculate solar position at specific time
timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)
position = calculate_solar_position(
    timestamp=timestamp,
    latitude=49.8,
    longitude=15.5,
    altitude=300
)

print(f"Azimuth: {position.azimuth:.2f}°")
print(f"Elevation: {position.elevation:.2f}°")
print(f"Zenith: {position.zenith:.2f}°")
```

### Clear-Sky Irradiance Calculation

```python
from pvsolarsim.atmosphere import calculate_clearsky_irradiance

# Calculate clear-sky irradiance
irradiance = calculate_clearsky_irradiance(
    apparent_elevation=45.0,
    latitude=49.8,
    longitude=15.5,
    altitude=300,
    model="ineichen",
    linke_turbidity=3.0
)

print(f"GHI: {irradiance.ghi:.2f} W/m²")
print(f"DNI: {irradiance.dni:.2f} W/m²")
print(f"DHI: {irradiance.dhi:.2f} W/m²")
```

### Plane-of-Array (POA) Irradiance

```python
from pvsolarsim.irradiance import calculate_poa_irradiance

# Calculate irradiance on tilted panel
poa = calculate_poa_irradiance(
    surface_tilt=35.0,        # Panel tilt angle
    surface_azimuth=180.0,    # South-facing
    solar_zenith=position.zenith,
    solar_azimuth=position.azimuth,
    dni=irradiance.dni,
    ghi=irradiance.ghi,
    dhi=irradiance.dhi,
    diffuse_model="perez",    # Industry standard
    albedo=0.2                # Ground reflectance
)

print(f"POA Direct:   {poa.poa_direct:.2f} W/m²")
print(f"POA Diffuse:  {poa.poa_diffuse:.2f} W/m²")
print(f"POA Ground:   {poa.poa_ground:.2f} W/m²")
print(f"POA Global:   {poa.poa_global:.2f} W/m²")
```

### Cell Temperature Modeling

```python
from pvsolarsim import calculate_cell_temperature, calculate_temperature_correction_factor

# Calculate cell temperature using Faiman model (default)
cell_temp = calculate_cell_temperature(
    poa_global=800,      # W/m²
    temp_air=25,         # °C
    wind_speed=3         # m/s
)
print(f"Cell temperature: {cell_temp:.2f}°C")

# Calculate temperature correction factor for power
correction = calculate_temperature_correction_factor(
    cell_temperature=cell_temp,
    temp_coefficient=-0.004  # -0.4%/°C for c-Si
)
print(f"Power correction: {correction:.4f}")  # e.g., 0.92 = 92% of STC power

# Use different models: 'faiman', 'sapm', 'pvsyst', 'generic_linear'
temp_sapm = calculate_cell_temperature(
    poa_global=800,
    temp_air=25,
    wind_speed=3,
    model='sapm'
)
print(f"SAPM cell temperature: {temp_sapm:.2f}°C")
```

### Instantaneous Power Calculation

```python
from pvsolarsim import Location, PVSystem, calculate_power
from datetime import datetime
import pytz

# Define location
location = Location(
    latitude=49.8,
    longitude=15.5,
    altitude=300,
    timezone="Europe/Prague"
)

# Define PV system
system = PVSystem(
    panel_area=20.0,        # m²
    panel_efficiency=0.20,  # 20%
    tilt=35.0,              # degrees
    azimuth=180.0,          # South-facing
    temp_coefficient=-0.004 # -0.4% per °C
)

# Calculate power at specific time
timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)
result = calculate_power(
    location=location,
    system=system,
    timestamp=timestamp,
    ambient_temp=25,      # °C
    wind_speed=3,         # m/s
    cloud_cover=0         # 0-100%
)

print(f"DC Power: {result.power_w:.2f} W ({result.power_w/1000:.2f} kW)")
print(f"POA Irradiance: {result.poa_irradiance:.2f} W/m²")
print(f"Cell Temperature: {result.cell_temperature:.2f}°C")
print(f"Solar Elevation: {result.solar_elevation:.2f}°")

# With cloud cover
result_cloudy = calculate_power(
    location, system, timestamp,
    ambient_temp=25, wind_speed=3, cloud_cover=50
)
print(f"Cloudy Power: {result_cloudy.power_w:.2f} W (50% cloud cover)")

# With soiling and degradation
result_aged = calculate_power(
    location, system, timestamp,
    soiling_factor=0.95,      # 5% soiling loss
    degradation_factor=0.97,  # 3% degradation
    inverter_efficiency=0.96  # 96% inverter efficiency
)
print(f"AC Power (aged system): {result_aged.power_ac_w:.2f} W")
```

### Annual Energy Simulation

```python
from pvsolarsim import Location, PVSystem, simulate_annual

# Define location and system
location = Location(
    latitude=40.0,
    longitude=-105.0,
    altitude=1655,
    timezone="America/Denver"
)

system = PVSystem(
    panel_area=20.0,        # m²
    panel_efficiency=0.20,  # 20%
    tilt=35.0,              # degrees
    azimuth=180.0,          # South-facing
    temp_coefficient=-0.004 # -0.4% per °C
)

# Simulate full year with 5-minute intervals
results = simulate_annual(
    location=location,
    system=system,
    year=2025,
    interval_minutes=5,
    weather_source="clear_sky"
)

# Display annual statistics
print(f"Total energy: {results.statistics.total_energy_kwh:.2f} kWh")
print(f"Capacity factor: {results.statistics.capacity_factor * 100:.2f}%")
print(f"Peak power: {results.statistics.peak_power_w:.0f} W")
print(f"Performance ratio: {results.statistics.performance_ratio:.2%}")

# Monthly energy production
for month, energy in results.statistics.monthly_energy_kwh.items():
    print(f"{month}: {energy:.2f} kWh")

# Export time series to CSV
results.export_csv("annual_production_2025.csv")

# With cloud cover, soiling, and inverter efficiency
results_realistic = simulate_annual(
    location=location,
    system=system,
    year=2025,
    interval_minutes=60,  # Hourly for faster simulation
    cloud_cover=30,       # 30% average cloud cover
    soiling_factor=0.98,  # 2% soiling loss
    inverter_efficiency=0.96  # 96% inverter efficiency
)
print(f"Realistic annual energy: {results_realistic.statistics.total_energy_kwh:.2f} kWh")
```

> **See more examples** in the [examples/](examples/) directory:
> - [annual_simulation_example.py](examples/annual_simulation_example.py) - Annual energy production simulation
> - [power_calculation_example.py](examples/power_calculation_example.py) - Comprehensive power calculation demonstrations
> - [poa_example.py](examples/poa_example.py) - POA irradiance calculations

## 📚 Documentation

- [Product Requirements Specification](PRODUCT_REQUIREMENTS.md)
- [Development Planning](PLANNING.md)
- [AI Development Instructions](copilot-instructions.md)
- [API Reference](https://pvsolarsim.readthedocs.io) *(coming soon)*
- [Examples](examples/) *(coming soon)*

## 🧪 Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=pvsolarsim --cov-report=html
```

Validate against pvlib:
```bash
pytest tests/validation/
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **pvlib-python**: Reference implementation for validation ([pvlib/pvlib-python](https://github.com/pvlib/pvlib-python))
- **NREL**: Solar Position Algorithm and atmospheric models
- **Community**: All contributors and users

## 🔗 Related Projects

- [PVSolarSim Web App](https://github.com/jenicek001/pvsolarsim-webapp) - User-friendly web interface for non-technical users

## 📧 Contact

- **Author**: jenicek001
- **Issues**: [GitHub Issues](https://github.com/jenicek001/pvsolarsim/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jenicek001/pvsolarsim/discussions)

---

**Made with ☀️ for a sustainable energy future**
