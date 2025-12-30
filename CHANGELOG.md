# Changelog

All notable changes to PVSolarSim will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-12-30

First alpha release of PVSolarSim.

### Added

**Core Functionality**
- Solar position calculations using NREL SPA algorithm (via pvlib)
- Clear-sky irradiance models (Ineichen and Simplified Solis)
- Cloud cover modeling (Campbell-Norman, Simple Linear, Kasten-Czeplak)
- Plane-of-array (POA) irradiance for tilted surfaces
- Multiple diffuse transposition models (Isotropic, Perez, Hay-Davies)
- Incidence angle modifiers (ASHRAE, Physical, Martin-Ruiz)
- Cell temperature models (Faiman, SAPM, PVsyst, Generic Linear)
- Instantaneous power calculation
- Annual energy simulation with time series generation
- Statistical analysis (capacity factor, performance ratio, etc.)

**Weather Integration**
- CSV and JSON weather data readers
- PVGIS TMY data client
- OpenWeatherMap API client
- Weather data caching
- Data interpolation and gap filling
- Quality checks and validation

**Data Models**
- Location dataclass with validation
- PVSystem dataclass with validation
- Comprehensive result dataclasses

**Documentation**
- Complete API reference with Sphinx
- User guide with installation, quick start, and core concepts
- Advanced usage examples
- Jupyter notebook tutorials
- Mathematical background documentation
- FAQ and troubleshooting guide
- Contributing guidelines

**Testing**
- 270+ comprehensive tests
- 81%+ code coverage
- Validation against pvlib-python
- Performance benchmarks

**Development Tools**
- Black code formatter
- Ruff linter
- mypy type checker
- Pre-commit hooks
- GitHub Actions CI/CD

## [0.0.1] - 2025-12-23

- Initial project setup
- Repository structure created
- Basic package scaffold

---

## Roadmap

See [PLANNING.md](PLANNING.md) for the full development roadmap.

### Upcoming Releases

**v0.9.0 (Beta) - Q1 2026**
- PyPI publication
- Read the Docs hosting
- Additional examples and tutorials
- Performance optimizations

**v1.0.0 (Stable) - Q1 2026**
- Production-ready release
- >90% test coverage
- Complete documentation
- Validated against multiple data sources

**v1.1.0 and beyond**
- Shade analysis
- Bifacial panel support
- Economic analysis (LCOE, ROI)
- Battery storage simulation
- Machine learning integration
