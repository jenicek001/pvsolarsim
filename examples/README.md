# PVSolarSim Examples

This directory contains example scripts demonstrating the functionality of PVSolarSim.

## Available Examples

### 1. `basic_example.py`

Demonstrates core functionality:
- Solar position calculations throughout the day
- Clear-sky irradiance calculations
- Comparison of different clear-sky models (Ineichen vs Simplified Solis)
- Effect of atmospheric turbidity on irradiance

**Run it:**
```bash
python examples/basic_example.py
```

### 2. `poa_example.py` ✨ NEW

Comprehensive plane-of-array (POA) irradiance demonstrations:
- POA irradiance calculation for tilted panels
- Comparison of diffuse transposition models (Isotropic, Perez, Hay-Davies)
- Effect of ground albedo on irradiance
- Incidence angle modifier (IAM) model comparison
- Daily POA irradiance profile

**Run it:**
```bash
python examples/poa_example.py
```

**Key topics covered:**
- Angle of incidence calculations
- Diffuse sky models (isotropic vs anisotropic)
- Ground-reflected irradiance
- IAM losses at high angles
- Time-of-day variation

### 3. `integration_example.py` ✨ NEW

Complete workflow demonstration integrating all implemented features:
- Location and PV system definition
- Solar position tracking
- Clear-sky irradiance modeling
- POA irradiance on tilted panels
- Simplified DC power estimation
- Daily energy production profile
- Orientation comparison study

**Run it:**
```bash
python examples/integration_example.py
```

**Demonstrates:**
- Complete analysis workflow from location to power
- Summer solstice case study
- Hourly profile for full day
- Impact of panel orientation on production
- Practical insights and takeaways

## Coming Soon

- **temperature_modeling.py** - Cell temperature effects on performance (Week 5)
- **power_calculation.py** - Full instantaneous power calculation (Week 6)
- **annual_simulation.py** - Full year simulation with weather data (Week 7)
- **comparison_study.py** - Compare different PV system configurations
- **weather_integration.py** - Using real weather data from APIs (Week 8-9)
- **optimization.py** - Finding optimal tilt and azimuth angles

## Requirements

All examples use only the installed `pvsolarsim` package. Make sure to install it first:

```bash
pip install -e .
```

Or for development:

```bash
pip install -e ".[dev]"
```

## Example Output

Each example produces detailed console output with:
- Formatted tables showing calculations
- Physical insights and interpretations
- Comparison studies
- Key takeaways

Examples are designed to be educational and demonstrate best practices for using PVSolarSim.
