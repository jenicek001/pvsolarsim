Changelog
=========

All notable changes to PVSolarSim will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[Unreleased]
------------

[0.1.0] - 2025-12-30
--------------------

First alpha release of PVSolarSim.

Added
~~~~~

**Core Functionality**

* Solar position calculations using NREL SPA algorithm (via pvlib)
* Clear-sky irradiance models (Ineichen and Simplified Solis)
* Cloud cover modeling (Campbell-Norman, Simple Linear, Kasten-Czeplak)
* Plane-of-array (POA) irradiance for tilted surfaces
* Multiple diffuse transposition models (Isotropic, Perez, Hay-Davies)
* Incidence angle modifiers (ASHRAE, Physical, Martin-Ruiz)
* Cell temperature models (Faiman, SAPM, PVsyst, Generic Linear)
* Instantaneous power calculation
* Annual energy simulation with time series generation
* Statistical analysis (capacity factor, performance ratio, etc.)

**Weather Integration**

* CSV and JSON weather data readers
* PVGIS TMY data client
* OpenWeatherMap API client
* Weather data caching
* Data interpolation and gap filling
* Quality checks and validation

**Data Models**

* Location dataclass with validation
* PVSystem dataclass with validation
* Comprehensive result dataclasses

**Documentation**

* Complete API reference with Sphinx
* User guide with installation, quick start, and core concepts
* Advanced usage examples
* Jupyter notebook tutorials (5 notebooks)
* Mathematical background documentation
* FAQ and troubleshooting guide
* Contributing guidelines

**Testing**

* 270+ comprehensive tests
* 81%+ code coverage
* Validation against pvlib-python
* Performance benchmarks

**Development Tools**

* Black code formatter
* Ruff linter
* mypy type checker
* Pre-commit hooks
* GitHub Actions CI/CD

Fixed
~~~~~

* N/A (initial release)

Changed
~~~~~~~

* N/A (initial release)

Deprecated
~~~~~~~~~~

* N/A (initial release)

Removed
~~~~~~~

* N/A (initial release)

Security
~~~~~~~~

* N/A (initial release)

[0.0.1] - 2025-12-23
--------------------

* Initial project setup
* Repository structure created
* Basic package scaffold

---

## Release Notes

### v0.1.0 Alpha Release

This is the first public alpha release of PVSolarSim. It includes all core functionality for PV simulation:

**Highlights:**

* High-accuracy solar position (<0.01° error)
* Multiple validated clear-sky and temperature models
* Complete annual simulation capability
* Weather data integration (CSV, JSON, PVGIS, OpenWeatherMap)
* Comprehensive documentation and examples
* Well-tested (270+ tests, 81%+ coverage)

**Known Limitations:**

* PyPI package not yet published (install from GitHub)
* Some advanced features deferred to future versions
* Documentation hosted locally only (Read the Docs coming soon)

**Installation:**

.. code-block:: bash

   git clone https://github.com/jenicek001/pvsolarsim.git
   cd pvsolarsim
   pip install -e ".[dev]"

**Quick Example:**

.. code-block:: python

   from pvsolarsim import Location, PVSystem, simulate_annual

   location = Location(latitude=40.0, longitude=-105.0, altitude=1655)
   system = PVSystem(panel_area=20.0, panel_efficiency=0.20, tilt=35, azimuth=180)

   results = simulate_annual(location, system, 2025, weather_source='clear_sky')
   print(f"Annual energy: {results.statistics.total_energy_kwh:.2f} kWh")

**Feedback:**

Please report issues on GitHub: https://github.com/jenicek001/pvsolarsim/issues

---

## Version Numbering

PVSolarSim follows Semantic Versioning (SemVer):

* **MAJOR** version: Incompatible API changes
* **MINOR** version: New functionality (backward compatible)
* **PATCH** version: Bug fixes (backward compatible)

Pre-release versions use suffixes:

* ``-alpha``: Early development, unstable
* ``-beta``: Feature complete, testing phase
* ``-rc``: Release candidate, final testing

---

## Roadmap

See PLANNING.md for the full development roadmap.

### Upcoming Releases

**v0.9.0 (Beta) - Q1 2026**

* PyPI publication
* Read the Docs hosting
* Additional examples and tutorials
* Performance optimizations

**v1.0.0 (Stable) - Q1 2026**

* Production-ready release
* >90% test coverage
* Complete documentation
* Validated against multiple data sources

**v1.1.0 and beyond**

* Shade analysis
* Bifacial panel support
* Economic analysis (LCOE, ROI)
* Battery storage simulation
* Machine learning integration
