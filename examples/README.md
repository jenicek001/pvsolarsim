# PVSolarSim Examples

This directory contains example scripts demonstrating the functionality of PVSolarSim.

## Available Examples

### 1. `basic_example.py`

Demonstrates core functionality:
- Solar position calculations throughout the day
- Clear-sky irradiance calculations
- Comparison of different clear-sky models
- Effect of atmospheric turbidity on irradiance

**Run it:**
```bash
python examples/basic_example.py
```

## Coming Soon

- **power_calculation.py** - Instantaneous power calculation with temperature effects
- **annual_simulation.py** - Full year simulation with weather data
- **comparison_study.py** - Compare different PV system configurations
- **weather_integration.py** - Using real weather data from APIs
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
