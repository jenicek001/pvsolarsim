"""Weather data integration for PVSolarSim.

This module provides interfaces and implementations for fetching weather data
from various sources including APIs, files, and databases. It supports:

- CSV file reading with custom column mapping
- JSON file reading
- OpenWeatherMap Solar API integration
- PVGIS TMY data integration
- Data validation and quality checks
- Caching for API responses

Examples
--------
>>> from pvsolarsim.weather import CSVWeatherReader
>>> reader = CSVWeatherReader('weather.csv', column_mapping={'ghi': 'irradiance'})
>>> weather_data = reader.read()
>>>
>>> from pvsolarsim.weather import PVGISClient
>>> client = PVGISClient()
>>> weather_data = client.read_tmy(latitude=45.0, longitude=8.0)
"""

from pvsolarsim.weather.api_clients import OpenWeatherMapClient, PVGISClient
from pvsolarsim.weather.base import WeatherDataSource
from pvsolarsim.weather.cache import WeatherCache
from pvsolarsim.weather.readers import CSVWeatherReader, JSONWeatherReader

__all__ = [
    "WeatherDataSource",
    "CSVWeatherReader",
    "JSONWeatherReader",
    "OpenWeatherMapClient",
    "PVGISClient",
    "WeatherCache",
]
