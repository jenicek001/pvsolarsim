# AI Agent Instructions for PVSolarSim Python Library Development

**Project:** PVSolarSim - Photovoltaic Solar Simulation Library  
**Language:** Python 3.9+  
**Type:** PyPI Package  
**Purpose:** Calculate PV power output and simulate annual energy production

---

## Project Context

You are working on PVSolarSim, a Python library for accurate photovoltaic energy simulation. The library must be:
- **Accurate:** Validated against pvlib-python and real-world data
- **Fast:** Optimized for annual simulations with 5-minute intervals
- **User-friendly:** Simple API for common use cases, advanced API for researchers
- **Well-documented:** Comprehensive docs with examples and scientific background
- **Production-ready:** Suitable for PyPI publication with >90% test coverage

### Core Functionality
1. Solar position calculations (SPA algorithm)
2. Atmospheric modeling (clear-sky irradiance with multiple models)
3. Cloud cover effects on irradiance
4. Plane-of-array (POA) irradiance for tilted panels
5. Temperature-dependent panel performance
6. Instantaneous power calculation
7. Annual energy production simulation with weather integration

---

## Git Workflow & Branch Strategy

**Branch Model:**

This project uses a **single-branch workflow** optimized for GitHub Copilot automation:

- **`master`** - Main development and production branch
  - All feature PRs target `master` directly
  - GitHub Copilot creates feature branches and PRs to `master`
  - CI runs automatically on all PRs to `master`
  - Releases are tagged from `master` (e.g., v1.0.0)

**GitHub Copilot Workflow:**

1. Copilot creates feature branch: `copilot/feature-name`
2. Copilot implements changes and commits
3. Copilot creates PR targeting `master`
4. CI runs automatically (no manual approval needed)
5. Human reviews and merges PR
6. Feature branch auto-deleted after merge

**Why No Develop Branch?**

- Small team/solo development - no need for complex branching
- GitHub Copilot works best with direct-to-main workflow
- Faster iteration and simpler CI configuration
- `master` is always in releasable state (>90% test coverage enforced)

**CI/CD Configuration:**

- Workflow file: `.github/workflows/test.yml`
- Triggers: All pushes to `master` and `copilot/**` branches, all PRs to `master`
- No manual approval required for CI on PRs from `copilot/**` branches

---

## Development Environment Setup

**CRITICAL: Always Use Virtual Environment**

- **NEVER install packages system-wide** - Always use the project's virtual environment
- **Virtual environment location:** `.venv/` in the project root
- **Before any Python operation** (running tests, installing packages, executing scripts):
  1. Activate the virtual environment: `source .venv/bin/activate`
  2. Verify you're using the correct Python: `which python` should show `.venv/bin/python`

**Setup Commands:**
```bash
# Initial setup (if .venv doesn't exist)
cd /home/honzik/GitHub/pvsolarsim
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"

# Daily workflow (if .venv exists)
cd /home/honzik/GitHub/pvsolarsim
source .venv/bin/activate
# Now run tests, install packages, etc.
```

**When Running Commands:**
- ✅ **DO:** `source .venv/bin/activate && python test_pr1.py`
- ✅ **DO:** `source .venv/bin/activate && pytest`
- ✅ **DO:** `source .venv/bin/activate && pip install numpy`
- ❌ **DON'T:** `python test_pr1.py` (without activating venv)
- ❌ **DON'T:** `sudo pip install ...` (NEVER use sudo for Python packages)

**Verification:**
```bash
# Always verify before running code
which python  # Should output: /home/honzik/GitHub/pvsolarsim/.venv/bin/python
pip list      # Should show project dependencies in isolation
```

---

## Project Organization

### File Structure Principles

**CRITICAL: Keep root directory clean and organized**

**Root Directory Guidelines:**
- ✅ **Keep in root:** Core project files only (README.md, LICENSE, pyproject.toml, PLANNING.md, PRODUCT_REQUIREMENTS.md)
- ❌ **Never in root:** Implementation status files, test result documents, integration test scripts

**Proper File Organization:**
```
pvsolarsim/
├── docs/                       # All documentation
│   ├── implementation/         # Implementation status, PR results
│   │   ├── PR*_TEST_RESULTS.md
│   │   ├── WEEK*_IMPLEMENTATION_SUMMARY.md
│   │   └── IMPLEMENTATION_SUMMARY.md
│   └── api/                    # Sphinx-generated API docs (when added)
├── tests/
│   ├── integration/            # Integration tests (test_pr*.py, etc.)
│   │   ├── test_pr1.py
│   │   ├── test_pr2.py
│   │   └── ...
│   ├── test_*.py               # Unit tests only
│   └── conftest.py
├── examples/                   # Example scripts for users
│   ├── basic_example.py
│   └── README.md
└── src/pvsolarsim/             # Package source code
```

**Rules for New Files:**
1. **Test Results/Reports:** Always → `docs/implementation/`
2. **Integration Tests:** Always → `tests/integration/`
3. **Unit Tests:** Always → `tests/` (not subdirectory)
4. **Examples:** Always → `examples/`
5. **Temporary Analysis:** Create in `.scratch/` (add to .gitignore)

**When Creating Files:**
- BEFORE creating a file, check if it belongs in a subdirectory
- Use descriptive filenames with clear purpose
- Add README.md in subdirectories to explain content

---

## Development Principles

### 1. Code Quality Standards

**Style Guide:**
- Follow PEP 8 strictly
- Use Black for formatting (line length: 100)
- Use Ruff for linting
- Type hints for all function signatures (PEP 484)
- Docstrings for all public APIs (NumPy style)

**Example:**
```python
def calculate_solar_position(
    timestamp: datetime,
    latitude: float,
    longitude: float,
    altitude: float = 0,
) -> SolarPosition:
    """
    Calculate solar position for given time and location.

    Uses the Solar Position Algorithm (SPA) for high accuracy (<0.01° error).

    Parameters
    ----------
    timestamp : datetime
        Time of calculation (must be timezone-aware)
    latitude : float
        Latitude in decimal degrees (-90 to 90, North positive)
    longitude : float
        Longitude in decimal degrees (-180 to 180, East positive)
    altitude : float, optional
        Altitude above sea level in meters (default: 0)

    Returns
    -------
    SolarPosition
        Dataclass containing azimuth, zenith, elevation, etc.

    Raises
    ------
    ValueError
        If latitude or longitude out of valid range

    Examples
    --------
    >>> from datetime import datetime
    >>> timestamp = datetime(2025, 6, 21, 12, 0, tzinfo='UTC')
    >>> pos = calculate_solar_position(timestamp, 49.8, 15.5, 300)
    >>> print(f"Azimuth: {pos.azimuth:.2f}°")
    Azimuth: 183.45°

    References
    ----------
    .. [1] Reda, I., & Andreas, A. (2004). Solar position algorithm for solar
           radiation applications. Solar Energy, 76(5), 577-589.
    """
    # Implementation here
    pass
```

### 2. Architecture Principles

**Modularity:**
- Separate concerns into distinct modules
- Keep modules focused and cohesive
- Avoid circular dependencies

**Modularity:**
- Use dataclasses for configuration and results
- Prefer composition over inheritance
- Use strategy pattern for swappable algorithms (e.g., clear-sky models)

**Example:**
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class IrradianceComponents:
    """Irradiance components (GHI, DNI, DHI)."""
    ghi: float  # Global Horizontal Irradiance (W/m²)
    dni: float  # Direct Normal Irradiance (W/m²)
    dhi: float  # Diffuse Horizontal Irradiance (W/m²)

class ClearSkyModel(ABC):
    """Base class for clear-sky irradiance models."""

    @abstractmethod
    def calculate(
        self,
        apparent_elevation: float,
        **kwargs
    ) -> IrradianceComponents:
        """Calculate clear-sky irradiance."""
        pass

class SimplifiedSolis(ClearSkyModel):
    """Simplified Solis clear-sky model."""

    def calculate(
        self,
        apparent_elevation: float,
        aod700: float,
        precipitable_water: float,
        pressure: float
    ) -> IrradianceComponents:
        # Implementation
        pass
```

### 3. Testing Requirements

**Coverage Target:** >90% for all modules

**Test Structure:**
```
tests/
├── unit/
│   ├── test_solar_position.py
│   ├── test_clearsky.py
│   ├── test_poa.py
│   └── test_temperature.py
├── integration/
│   ├── test_power_calculation.py
│   └── test_annual_simulation.py
├── validation/
│   ├── test_vs_pvlib.py
│   └── test_vs_measured_data.py
└── conftest.py  # Shared fixtures
```

**Test Example:**
```python
import pytest
import numpy as np
from datetime import datetime
from pvsolarsim.solar import calculate_solar_position

class TestSolarPosition:
    """Test suite for solar position calculations."""

    def test_solar_position_basic(self):
        """Test basic solar position calculation."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo='UTC')
        pos = calculate_solar_position(timestamp, 40.0, -105.0, 1655)

        assert 150 < pos.azimuth < 210  # Roughly south at noon
        assert 70 < pos.elevation < 80  # High summer elevation
        assert pos.zenith == pytest.approx(90 - pos.elevation, abs=0.01)

    def test_solar_position_sunrise(self):
        """Test solar position at sunrise."""
        # Expected sunrise time at this location
        timestamp = datetime(2025, 6, 21, 5, 30, tzinfo='America/Denver')
        pos = calculate_solar_position(timestamp, 40.0, -105.0, 1655)

        assert pos.elevation < 1  # Near horizon
        assert 50 < pos.azimuth < 90  # Northeast

    @pytest.mark.parametrize("latitude,expected_max_elevation", [
        (0, 90),    # Equator on equinox
        (40, 73.5), # 40°N on summer solstice
        (66.5, 47), # Arctic circle on summer solstice
    ])
    def test_solar_elevation_by_latitude(self, latitude, expected_max_elevation):
        """Test maximum solar elevation varies with latitude."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo='UTC')
        pos = calculate_solar_position(timestamp, latitude, 0, 0)

        assert pos.elevation == pytest.approx(expected_max_elevation, abs=2)

    def test_invalid_latitude(self):
        """Test error handling for invalid latitude."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo='UTC')

        with pytest.raises(ValueError, match="Latitude must be between"):
            calculate_solar_position(timestamp, 95.0, 0, 0)

        with pytest.raises(ValueError, match="Latitude must be between"):
            calculate_solar_position(timestamp, -95.0, 0, 0)
```

**Always Write Tests For:**
- Edge cases (sunrise, sunset, midnight, polar regions)
- Invalid inputs (out-of-range values, None, wrong types)
- Vectorized operations (ensure NumPy arrays work)
- Performance (benchmark critical paths)

### 4. Performance Optimization

**Vectorization:**
- Use NumPy arrays for batch operations
- Avoid Python loops for large datasets
- Leverage pandas for time series

**Example:**
```python
def calculate_power_series(
    timestamps: pd.DatetimeIndex,
    location: Location,
    system: PVSystem,
    weather_data: pd.DataFrame
) -> pd.Series:
    """
    Calculate power for time series (vectorized).

    This is much faster than looping over timestamps.
    """
    # Vectorized solar position calculation
    solar_positions = calculate_solar_position_vectorized(
        timestamps, location.latitude, location.longitude, location.altitude
    )

    # Vectorized irradiance calculation
    irradiance = calculate_irradiance_vectorized(
        solar_positions, weather_data
    )

    # Vectorized power calculation
    power = (irradiance.poa_global *
             system.panel_area *
             system.panel_efficiency *
             temperature_correction_factor)

    return pd.Series(power, index=timestamps, name='power_w')
```

**Profiling:**
- Use `cProfile` for profiling
- Identify bottlenecks before optimizing
- Measure impact of optimizations

```python
# In tests or benchmarks
import cProfile
import pstats

def profile_simulation():
    profiler = cProfile.Profile()
    profiler.enable()

    # Run simulation
    results = simulate_annual(...)

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
```

### 5. Documentation Standards

**README.md Must Include:**
- Installation instructions
- Quick start example
- Features list
- Links to documentation
- Citation information
- Badges (CI, coverage, PyPI version)

**API Documentation (Sphinx):**
- Auto-generated from docstrings
- Mathematical formulas using LaTeX
- References to scientific papers
- Examples in docstrings

**Example Docstring with Math:**
```python
def airmass_absolute(airmass_relative: float, pressure: float) -> float:
    """
    Calculate absolute air mass from relative air mass and pressure.

    The absolute air mass accounts for atmospheric pressure variation
    with altitude. It's defined as:

    .. math::

        AM_{abs} = AM_{rel} \\frac{P}{P_0}

    where :math:`P_0 = 101325` Pa is standard pressure at sea level.

    Parameters
    ----------
    airmass_relative : float
        Relative air mass (dimensionless)
    pressure : float
        Atmospheric pressure in Pascals

    Returns
    -------
    float
        Absolute air mass (dimensionless)

    References
    ----------
    .. [1] Kasten, F., & Young, A. T. (1989). Revised optical air mass
           tables and approximation formula. Applied Optics, 28(22), 4735-4738.
    """
    P0 = 101325  # Standard pressure (Pa)
    return airmass_relative * pressure / P0
```

---

## Implementation Guidelines

### When Implementing Solar Position Module

**Key Requirements:**
- Use Solar Position Algorithm (SPA) for accuracy
- Support single timestamp and time series (vectorized)
- Handle timezone conversions properly
- Validate input ranges
- Return comprehensive `SolarPosition` dataclass

**Consider:**
- Option to use pvlib.solarposition as dependency (fast, validated)
- Or implement from scratch (no external dependency, educational)
- Recommendation: Use pvlib initially, make pluggable later

**Validation:**
- Test against NREL SPA test cases
- Accuracy target: <0.01° error

### When Implementing Clear-Sky Models

**Models to Support:**
1. **Simplified Solis** - Good balance of accuracy and speed
2. **Ineichen** - Industry standard, uses Linke turbidity
3. **Bird** - Simple, good for validation

**Key Requirements:**
- Strategy pattern for swappable models
- Consistent interface (all return `IrradianceComponents`)
- Support both single-point and vectorized calculations
- Validate against pvlib results

**Example:**
```python
# User can choose model
clear_sky = ClearSkyModel(model='simplified_solis')
irradiance = clear_sky.calculate(elevation=45, aod700=0.1, ...)

# Or explicitly
from pvsolarsim.atmosphere import SimplifiedSolis
model = SimplifiedSolis()
irradiance = model.calculate(elevation=45, aod700=0.1, ...)
```

### When Implementing POA Irradiance

**Diffuse Models to Support:**
- Isotropic (simplest)
- Hay-Davies
- Perez (recommended default)
- Klucher
- Reindl

**IAM Models:**
- ASHRAE (simple)
- Physical (Fresnel-based)
- Martin-Ruiz
- SAPM (optional)

**Key Calculations:**
1. Angle of incidence (AOI)
2. Beam component: `DNI * cos(AOI)`
3. Diffuse component (model-dependent)
4. Ground-reflected: `GHI * albedo * (1 - cos(tilt)) / 2`
5. Apply IAM to reduce beam at high angles

**Validate:**
- Compare with pvlib.irradiance.get_total_irradiance
- Test different tilt/azimuth combinations

### When Implementing Weather Integration

**API Clients:**
- Use `requests` with retry logic
- Implement rate limiting (respect API quotas)
- Cache responses (Redis or local cache)
- Handle API errors gracefully

**Example:**
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class OpenWeatherMapClient:
    """Client for OpenWeatherMap Solar API."""

    def __init__(self, api_key: str, cache_ttl: int = 86400):
        self.api_key = api_key
        self.cache_ttl = cache_ttl
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create session with retry logic."""
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def fetch_solar_radiation(
        self,
        latitude: float,
        longitude: float,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """Fetch solar radiation data."""
        # Check cache first
        cache_key = f"{latitude}_{longitude}_{start_date}_{end_date}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # API request
        url = "https://api.openweathermap.org/data/2.5/solar_radiation"
        params = {
            'lat': latitude,
            'lon': longitude,
            'start': int(start_date.timestamp()),
            'end': int(end_date.timestamp()),
            'appid': self.api_key
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            raise WeatherAPIError(f"Failed to fetch data: {e}")

        # Parse and cache
        df = self._parse_response(data)
        self._save_to_cache(cache_key, df)
        return df
```

### When Implementing Annual Simulation

**Design Principles:**
- Generate time series with timezone awareness
- Batch processing for performance
- Progress callbacks for long simulations
- Graceful handling of missing weather data

**Example:**
```python
def simulate_annual(
    location: Location,
    system: PVSystem,
    year: int,
    interval: str = '5min',
    weather_source: str = 'clear_sky',
    progress_callback: Optional[Callable[[float], None]] = None,
    **weather_kwargs
) -> SimulationResult:
    """
    Simulate annual PV energy production.

    Parameters
    ----------
    location : Location
        Geographic location
    system : PVSystem
        PV system configuration
    year : int
        Year to simulate
    interval : str, default '5min'
        Time interval ('1min', '5min', '15min', 'H')
    weather_source : str, default 'clear_sky'
        Weather data source ('clear_sky', 'openweathermap', 'pvgis', 'csv')
    progress_callback : callable, optional
        Function called with progress (0.0 to 1.0)
    **weather_kwargs
        Additional arguments for weather source (e.g., api_key, file_path)

    Returns
    -------
    SimulationResult
        Results including time series and summary statistics
    """
    # Generate time series
    times = pd.date_range(
        start=f'{year}-01-01',
        end=f'{year}-12-31 23:59:59',
        freq=interval,
        tz=location.timezone
    )

    # Fetch weather data
    weather_data = fetch_weather(
        location, times, weather_source, **weather_kwargs
    )

    # Simulate (vectorized)
    results = []
    total_steps = len(times)

    for i, chunk in enumerate(chunk_times(times, chunk_size=1000)):
        chunk_weather = weather_data.loc[chunk]
        chunk_results = calculate_power_series(
            chunk, location, system, chunk_weather
        )
        results.append(chunk_results)

        if progress_callback:
            progress = (i + 1) * 1000 / total_steps
            progress_callback(min(progress, 1.0))

    # Combine and analyze
    power_series = pd.concat(results)
    statistics = calculate_statistics(power_series)

    return SimulationResult(
        time_series=power_series,
        statistics=statistics,
        config={'location': location, 'system': system}
    )
```

---

## Code Review Checklist

Before committing, ensure:

- [ ] **Code Quality**
  - [ ] Follows PEP 8 (run `black` and `ruff`)
  - [ ] Type hints on all functions
  - [ ] NumPy-style docstrings with examples
  - [ ] No hardcoded values (use constants)

- [ ] **Testing**
  - [ ] Unit tests written for new functions
  - [ ] Tests pass locally (`pytest`)
  - [ ] Edge cases covered
  - [ ] Validation tests if applicable

- [ ] **Documentation**
  - [ ] Docstrings complete and accurate
  - [ ] Examples in docstrings work
  - [ ] README updated if API changed
  - [ ] Mathematical formulas documented

- [ ] **Performance**
  - [ ] Vectorized where possible (no unnecessary loops)
  - [ ] No obvious bottlenecks
  - [ ] Memory-efficient for large datasets

- [ ] **Compatibility**
  - [ ] Works with NumPy arrays and pandas Series
  - [ ] Handles timezone-aware datetimes
  - [ ] Cross-platform (no OS-specific code)

---

## Common Pitfalls to Avoid

### 1. Timezone Issues
```python
# ❌ Bad: Naive datetime
timestamp = datetime(2025, 6, 21, 12, 0)

# ✅ Good: Timezone-aware
import pytz
timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

# Or
timestamp = pd.Timestamp('2025-06-21 12:00', tz='UTC')
```

### 2. Angle Units Confusion
```python
# Always document if angles are in degrees or radians

# ❌ Bad: Unclear
def cos_aoi(sun_zenith, panel_tilt):
    return np.cos(sun_zenith - panel_tilt)  # Is this degrees or radians?

# ✅ Good: Clear
def cos_aoi_degrees(sun_zenith_deg: float, panel_tilt_deg: float) -> float:
    """Calculate cosine of angle of incidence.

    Parameters are in degrees, converted to radians internally.
    """
    return np.cos(np.radians(sun_zenith_deg - panel_tilt_deg))
```

### 3. Not Handling NaN/Inf
```python
# ❌ Bad: Division without checking
def clearness_index(ghi, ghi_clearsky):
    return ghi / ghi_clearsky  # Can produce inf or nan

# ✅ Good: Handle edge cases
def clearness_index(ghi: np.ndarray, ghi_clearsky: np.ndarray) -> np.ndarray:
    """Calculate clearness index, handling zero clear-sky irradiance."""
    with np.errstate(divide='ignore', invalid='ignore'):
        kt = ghi / ghi_clearsky
    kt = np.where(ghi_clearsky > 0, kt, 0)  # Set to 0 where clear-sky is 0
    return np.clip(kt, 0, 1.2)  # Clip to realistic range
```

### 4. Not Validating Inputs
```python
# ❌ Bad: No validation
def calculate_power(poa_irradiance, panel_area, efficiency):
    return poa_irradiance * panel_area * efficiency

# ✅ Good: Validate
def calculate_power(
    poa_irradiance: float,
    panel_area: float,
    efficiency: float
) -> float:
    """Calculate DC power output."""
    if poa_irradiance < 0:
        raise ValueError("Irradiance cannot be negative")
    if not 0 < panel_area < 10000:
        raise ValueError("Panel area must be between 0 and 10000 m²")
    if not 0 < efficiency < 1:
        raise ValueError("Efficiency must be between 0 and 1")

    return poa_irradiance * panel_area * efficiency
```

---

## Useful Resources

### Scientific References
- **Solar Position:** Reda & Andreas (2004) - NREL SPA algorithm
- **Clear-Sky Models:** Ineichen & Perez (2002), Bird & Hulstrom (1981)
- **POA Irradiance:** Perez et al. (1990), Hay & Davies (1980)
- **Temperature:** King et al. (2004) - SAPM model

### Python Libraries for Reference
- **pvlib-python:** https://pvlib-python.readthedocs.io/
- **PySAM:** https://nrel-pysam.readthedocs.io/
- **NumPy:** https://numpy.org/doc/
- **Pandas:** https://pandas.pydata.org/docs/

### Tools
- **Black:** Code formatter
- **Ruff:** Fast Python linter
- **mypy:** Static type checker
- **pytest:** Testing framework
- **Sphinx:** Documentation generator

---

## Questions to Ask During Development

1. **Is this function vectorized?** Can it handle NumPy arrays efficiently?
2. **Are units clear?** Degrees vs. radians? Watts vs. kilowatts?
3. **Is this validated?** Have I tested against pvlib or reference data?
4. **Is this documented?** Docstring with example and references?
5. **Is this fast enough?** Profiled for bottlenecks?
6. **Are edge cases handled?** Sunrise, sunset, polar regions, zero irradiance?

---

## Example: Complete Module Implementation

Here's how a complete module should look:

```python
"""
Solar position calculations using the Solar Position Algorithm (SPA).

This module provides functions to calculate the position of the sun
for any location and time on Earth. The implementation follows the
NREL SPA algorithm for high accuracy.

References
----------
.. [1] Reda, I., & Andreas, A. (2004). Solar position algorithm for solar
       radiation applications. Solar Energy, 76(5), 577-589.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Union

import numpy as np
import pandas as pd

__all__ = ['SolarPosition', 'calculate_solar_position', 'calculate_solar_position_series']


@dataclass
class SolarPosition:
    """
    Solar position data.

    Attributes
    ----------
    azimuth : float
        Solar azimuth angle in degrees (0° = North, 90° = East)
    zenith : float
        Solar zenith angle in degrees (0° = overhead)
    elevation : float
        Solar elevation angle in degrees (90° - zenith)
    hour_angle : float
        Solar hour angle in degrees
    declination : float
        Solar declination angle in degrees
    """
    azimuth: float
    zenith: float
    elevation: float
    hour_angle: float
    declination: float


def calculate_solar_position(
    timestamp: datetime,
    latitude: float,
    longitude: float,
    altitude: float = 0,
) -> SolarPosition:
    """
    Calculate solar position for a single timestamp.

    [Full docstring as shown earlier...]
    """
    # Validate inputs
    if not -90 <= latitude <= 90:
        raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
    if not -180 <= longitude <= 180:
        raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")
    if not timestamp.tzinfo:
        raise ValueError("timestamp must be timezone-aware")

    # Implementation (delegated to pvlib or custom)
    # ... actual calculation code ...

    return SolarPosition(
        azimuth=azimuth,
        zenith=zenith,
        elevation=90 - zenith,
        hour_angle=hour_angle,
        declination=declination
    )


def calculate_solar_position_series(
    times: pd.DatetimeIndex,
    latitude: float,
    longitude: float,
    altitude: float = 0,
) -> pd.DataFrame:
    """
    Calculate solar position for a time series (vectorized).

    This is much faster than calling calculate_solar_position in a loop.

    Parameters
    ----------
    times : pd.DatetimeIndex
        Time series (must be timezone-aware)
    latitude : float
        Latitude in decimal degrees
    longitude : float
        Longitude in decimal degrees
    altitude : float, optional
        Altitude in meters (default: 0)

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: azimuth, zenith, elevation, hour_angle, declination

    Examples
    --------
    >>> import pandas as pd
    >>> times = pd.date_range('2025-01-01', '2025-01-02', freq='H', tz='UTC')
    >>> df = calculate_solar_position_series(times, 40.0, -105.0, 1655)
    >>> df.head()
                              azimuth  zenith  elevation  ...
    2025-01-01 00:00:00+00:00   180.23  110.45     -20.45  ...
    """
    # Validate
    if not isinstance(times, pd.DatetimeIndex):
        raise TypeError("times must be pd.DatetimeIndex")
    if times.tz is None:
        raise ValueError("times must be timezone-aware")

    # Vectorized calculation
    # ... implementation ...

    return pd.DataFrame({
        'azimuth': azimuths,
        'zenith': zeniths,
        'elevation': elevations,
        'hour_angle': hour_angles,
        'declination': declinations
    }, index=times)


# Private helper functions
def _julian_day(timestamp: datetime) -> float:
    """Calculate Julian day number."""
    # Implementation
    pass


def _equation_of_time(julian_day: float) -> float:
    """Calculate equation of time."""
    # Implementation
    pass
```

---

## Maintaining Project Documentation

### Automatic PLANNING.md Updates

**CRITICAL:** After completing any implementation work, you MUST update [PLANNING.md](../PLANNING.md) to reflect what was actually implemented.

**When to Update PLANNING.md:**
- After completing any week's implementation tasks
- After finishing a phase or milestone
- After merging a PR that implements features
- When deviating from the original plan (document why)

**How to Update:**
1. **Mark completed tasks** with `[x]` checkboxes
2. **Update status indicators:**
   - ✅ COMPLETED for finished weeks
   - 🔄 IN PROGRESS for current work
   - ⬅️ NEXT for upcoming work
3. **Add implementation notes** where actual implementation differs from plan
   - Example: "Using pvlib instead of custom implementation"
   - Note deferred features with reasons
4. **Update metrics:**
   - Test coverage percentages
   - Number of tests
   - Performance benchmarks
5. **Update status header:**
   - Current version
   - Last updated date
   - Overall project status

**Template for Status Updates:**

```markdown
**Status:** ✅ COMPLETED (PR #X)
**Actual Implementation:** [Brief description if different from plan]
**Test Coverage:** X%
**Tests:** X tests passing
```

**Example of Good Update:**

```markdown
- [x] Implement Solar Position Algorithm (SPA)
  - ✅ Using pvlib.solarposition as dependency (validated, accurate)
  - Delegated to pvlib's NREL numpy implementation
  - Decision: No need for custom implementation, pvlib is industry standard

**Status:** ✅ COMPLETED (PR #1)
**Test Coverage:** 100%
**Tests:** 12 tests passing
```

**Never:**
- Leave PLANNING.md with outdated information
- Mark tasks complete without updating details
- Forget to document deviations from the plan

**Always:**
- Keep PLANNING.md in sync with reality
- Document architectural decisions
- Update success metrics as you go
- Note dependencies or blockers

---

**Remember:** The goal is production-quality code that others will trust and use. Every line should serve a purpose, be tested, and be documented. Think of future users (including future you) reading this code.

**When in doubt, refer to pvlib-python as a reference implementation.**

Good luck building PVSolarSim! 🌞
