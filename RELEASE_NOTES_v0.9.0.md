# Release Notes: PVSolarSim v0.9.0 Beta

**Release Date:** January 24, 2026  
**Version:** 0.9.0 (Beta)  
**Status:** Ready for testing and feedback

---

## 🎉 Overview

This is the first beta release of PVSolarSim! The library is now feature-complete and ready for early adopters and testers. We're excited to share this comprehensive Python library for photovoltaic solar energy simulation.

## ✨ What's New in v0.9.0

### Documentation & Examples
- **Complete API documentation** with Sphinx
- **Comprehensive user guide** covering installation, quick start, and core concepts
- **Advanced usage examples** and tutorials
- **Mathematical background** documentation for scientific validation
- **FAQ and troubleshooting guide** for common issues
- **Contributing guidelines** for community contributors

### Weather Integration Enhancements
- Improved weather data caching for better performance
- Enhanced data interpolation and gap filling algorithms
- Quality checks and validation for weather data
- Better error handling for API clients
- Support for multiple weather data sources (PVGIS, OpenWeatherMap, CSV/JSON)

### Testing & Validation
- **90.62% test coverage** (314 tests passing)
- Validation against pvlib-python for accuracy
- Performance benchmarks for optimization
- Comprehensive edge case testing

### Development Tools
- Pre-commit hooks configuration for code quality
- Automated code quality checks (Black, Ruff, mypy)
- GitHub Actions CI/CD improvements
- Multi-version Python testing support (3.9-3.12)

### GitHub Repository Improvements
- **Issue templates** for bug reports and feature requests
- Improved documentation organization
- Better contributor experience

## 🐛 Bug Fixes

- Fixed timezone handling in simulation results
- Improved error messages for invalid inputs
- Fixed edge cases in weather data interpolation
- Resolved pandas deprecation warnings

## 📦 Installation

### From PyPI (when released)
```bash
pip install pvsolarsim==0.9.0
```

### From Source
```bash
git clone https://github.com/jenicek001/pvsolarsim.git
cd pvsolarsim
pip install -e .
```

## 🚀 Quick Start

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
    tilt=35,                # degrees
    azimuth=180,            # South-facing
    inverter_efficiency=0.96
)

# Calculate power for a specific time
timestamp = datetime(2026, 6, 21, 12, 0, tzinfo=pytz.timezone("Europe/Prague"))
result = calculate_power(location, system, timestamp)

print(f"Power output: {result.power_w:.2f} W")
```

## 📊 Features

### Core Capabilities
- ✅ Solar position calculations using NREL SPA algorithm
- ✅ Clear-sky irradiance models (Ineichen, Simplified Solis)
- ✅ Cloud cover modeling (Campbell-Norman, Simple Linear, Kasten-Czeplak)
- ✅ Plane-of-array (POA) irradiance for tilted surfaces
- ✅ Multiple diffuse transposition models (Isotropic, Perez, Hay-Davies)
- ✅ Incidence angle modifiers (ASHRAE, Physical, Martin-Ruiz)
- ✅ Cell temperature models (Faiman, SAPM, PVsyst, Generic Linear)
- ✅ Instantaneous power calculation
- ✅ Annual energy simulation with time series generation
- ✅ Statistical analysis (capacity factor, performance ratio)

### Weather Integration
- ✅ CSV and JSON weather data readers
- ✅ PVGIS TMY data client
- ✅ OpenWeatherMap API client
- ✅ Weather data caching
- ✅ Data interpolation and gap filling
- ✅ Quality checks and validation

## ⚠️ Known Issues

- Sphinx documentation build generates some warnings (non-blocking)
- Weather API rate limiting not yet implemented
- Some pandas deprecation warnings in time series operations (will be addressed in v1.0.0)

## 🔮 What's Next (v1.0.0)

- Address all known issues
- Implement weather API rate limiting
- Resolve pandas deprecation warnings
- Additional validation against measured data
- Performance optimizations
- Expanded documentation and examples
- Target: March 2026

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### How You Can Help
- 🐛 Report bugs using the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- 💡 Suggest features using the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- 📖 Improve documentation
- 🧪 Add tests
- 💻 Submit pull requests

## 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for the complete changelog.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **pvlib-python** for the NREL SPA algorithm and validation reference
- NREL for solar radiation research and algorithms
- All contributors and testers

## 📧 Support

- **Issues:** [GitHub Issues](https://github.com/jenicek001/pvsolarsim/issues)
- **Discussions:** [GitHub Discussions](https://github.com/jenicek001/pvsolarsim/discussions)
- **Documentation:** [Read the Docs](https://pvsolarsim.readthedocs.io/) (coming soon)

---

**Please test this beta release and report any issues!** Your feedback is invaluable for making v1.0.0 production-ready.
