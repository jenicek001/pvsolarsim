# PVSolarSim

**Python library for photovoltaic (PV) solar energy simulation**

[![PyPI version](https://badge.fury.io/py/pvsolarsim.svg)](https://badge.fury.io/py/pvsolarsim)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🌞 Overview

PVSolarSim is a comprehensive Python library for simulating photovoltaic solar energy production. It provides accurate calculations for:

- **Solar position** (azimuth, zenith, elevation) using NREL's SPA algorithm
- **Atmospheric modeling** (Linke turbidity, aerosol optical depth, clear-sky irradiance)
- **Plane-of-array (POA) irradiance** with multiple diffuse models (Perez, Hay-Davies, Isotropic)
- **Cell temperature** modeling (SAPM, Faiman, King models)
- **Instantaneous power** calculation with temperature-dependent efficiency
- **Annual energy simulation** with configurable time intervals (1-60 minutes)
- **Weather integration** (OpenWeatherMap API, PVGIS TMY data, custom CSV files)

### Key Features

- ✅ **High Accuracy**: Solar position accuracy <0.01° using NREL SPA algorithm
- ✅ **Multiple Clear-Sky Models**: Ineichen (Linke turbidity), Simplified Solis (AOD), Bird (validation)
- ✅ **Flexible Weather Sources**: API integration, TMY data, custom CSV files
- ✅ **Vectorized Operations**: NumPy-based calculations for performance
- ✅ **Type-Safe**: Full type hints and runtime validation
- ✅ **Well-Tested**: >90% code coverage, validated against pvlib-python
- ✅ **Easy to Use**: High-level API for simple use cases, low-level API for advanced control

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

### Simple Instantaneous Power Calculation

```python
import pvsolarsim
from datetime import datetime

# Define location
location = pvsolarsim.Location(
    latitude=49.8,
    longitude=15.5,
    altitude=300,
    timezone="Europe/Prague"
)

# Define PV system
system = pvsolarsim.PVSystem(
    panel_area=20.0,        # m²
    panel_efficiency=0.20,  # 20%
    tilt=35.0,              # degrees
    azimuth=180.0,          # South-facing
    temp_coefficient=-0.004 # -0.4% per °C
)

# Calculate power at specific time
timestamp = datetime(2025, 6, 21, 12, 0)  # Summer solstice, noon
result = pvsolarsim.calculate_power(
    location=location,
    system=system,
    timestamp=timestamp,
    weather_source="clear_sky",
    clear_sky_model="ineichen"
)

print(f"Power: {result.power_w:.2f} W")
print(f"GHI: {result.ghi:.2f} W/m²")
print(f"POA: {result.poa_irradiance:.2f} W/m²")
print(f"Cell temp: {result.cell_temp_c:.2f} °C")
```

### Annual Energy Simulation

```python
# Run annual simulation with 5-minute intervals
results = pvsolarsim.simulate_annual(
    location=location,
    system=system,
    year=2025,
    interval=5,  # minutes
    weather_source="openweathermap",
    api_key="your_openweathermap_api_key"
)

# Print summary
print(f"Total energy: {results.total_energy_kwh:.2f} kWh/year")
print(f"Capacity factor: {results.capacity_factor:.2%}")
print(f"Peak power: {results.peak_power_w:.2f} W")

# Export to CSV
results.to_csv("annual_simulation.csv")

# Monthly breakdown
for month, energy in results.monthly_totals.items():
    print(f"{month}: {energy:.2f} kWh")
```

### Using Weather Data

```python
# Option 1: OpenWeatherMap API
results = pvsolarsim.simulate_annual(
    location=location,
    system=system,
    year=2025,
    weather_source="openweathermap",
    api_key="your_api_key"
)

# Option 2: PVGIS TMY data
results = pvsolarsim.simulate_annual(
    location=location,
    system=system,
    year=2025,
    weather_source="pvgis"
)

# Option 3: Custom CSV file
results = pvsolarsim.simulate_annual(
    location=location,
    system=system,
    year=2025,
    weather_source="csv",
    csv_path="my_weather_data.csv"
)
```

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
