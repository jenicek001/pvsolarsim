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
- ✅ **Location and PV system** data models with validation
- ✅ **High accuracy**: Solar position <0.01° error
- ✅ **Type-safe**: Full type hints with mypy validation
- ✅ **Well-tested**: 98% code coverage with 36 comprehensive tests

### Coming Soon (Roadmap)

- 🔄 **Plane-of-array (POA) irradiance** with multiple diffuse models (Week 4)
- 🔄 **Cell temperature** modeling (Week 5)
- 🔄 **Instantaneous power** calculation (Week 6)
- 🔄 **Annual energy simulation** (Week 7)
- 🔄 **Weather integration** (Weeks 8-9)

### Key Features

- ✅ **High Accuracy**: Solar position accuracy <0.01° using NREL SPA algorithm
- ✅ **Multiple Clear-Sky Models**: Ineichen (Linke turbidity), Simplified Solis (AOD)
- ✅ **Vectorized Operations**: NumPy-based calculations for performance
- ✅ **Type-Safe**: Full type hints and runtime validation
- ✅ **Well-Tested**: >95% code coverage, validated against pvlib-python
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

### Define Location and PV System

```python
from pvsolarsim import Location, PVSystem

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
```

> **Note**: Full power calculation and annual simulation features are coming in Phase 2 (Weeks 5-7).
> Currently available: Solar position calculations, clear-sky irradiance models, and core data models.

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
