"""Weather data integration for PVSolarSim.

This module provides interfaces and implementations for fetching weather data
from various sources including APIs, files, and databases. It supports:

- CSV file reading with custom column mapping
- JSON file reading
- OpenWeatherMap Solar API integration
- PVGIS TMY data integration
- Data validation and quality checks
- Caching for API responses
- Data interpolation and gap filling
- Quality flags and reporting

Examples
--------
>>> from pvsolarsim.weather import CSVWeatherReader
>>> reader = CSVWeatherReader('weather.csv', column_mapping={'ghi': 'irradiance'})
>>> weather_data = reader.read()
>>>
>>> from pvsolarsim.weather import PVGISClient
>>> client = PVGISClient()
>>> weather_data = client.read_tmy(latitude=45.0, longitude=8.0)
>>>
>>> from pvsolarsim.weather import interpolate_weather_data, perform_quality_checks
>>> filled_data = interpolate_weather_data(weather_data, method='linear')
>>> quality = perform_quality_checks(filled_data, latitude=45.0, longitude=8.0)
"""

from pvsolarsim.weather.api_clients import OpenWeatherMapClient, PVGISClient
from pvsolarsim.weather.base import WeatherDataSource
from pvsolarsim.weather.cache import WeatherCache
from pvsolarsim.weather.interpolation import (
    backward_fill,
    detect_gaps,
    fill_gaps,
    forward_fill,
    interpolate_weather_data,
)
from pvsolarsim.weather.quality import (
    QualityFlags,
    check_irradiance_consistency,
    check_negative_values,
    check_nighttime_irradiance,
    check_value_ranges,
    create_quality_report,
    perform_quality_checks,
)
from pvsolarsim.weather.readers import CSVWeatherReader, JSONWeatherReader

__all__ = [
    "WeatherDataSource",
    "CSVWeatherReader",
    "JSONWeatherReader",
    "OpenWeatherMapClient",
    "PVGISClient",
    "WeatherCache",
    # Interpolation
    "interpolate_weather_data",
    "forward_fill",
    "backward_fill",
    "detect_gaps",
    "fill_gaps",
    # Quality checks
    "perform_quality_checks",
    "QualityFlags",
    "check_nighttime_irradiance",
    "check_negative_values",
    "check_value_ranges",
    "check_irradiance_consistency",
    "create_quality_report",
]

