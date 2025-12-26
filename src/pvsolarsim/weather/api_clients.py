"""API clients for fetching weather data from external services.

This module provides clients for various weather data APIs including
OpenWeatherMap, PVGIS, and others.
"""

from datetime import datetime
from typing import Optional

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pvsolarsim.weather.base import WeatherDataSource
from pvsolarsim.weather.cache import WeatherCache


class OpenWeatherMapClient(WeatherDataSource):
    """Client for OpenWeatherMap Solar Radiation API.

    Fetches historical solar radiation data from OpenWeatherMap's API.
    Requires an API key which can be obtained from openweathermap.org.

    Parameters
    ----------
    api_key : str
        OpenWeatherMap API key
    cache_ttl : int, optional
        Cache time-to-live in seconds (default: 86400 = 24 hours)
    timeout : int, optional
        Request timeout in seconds (default: 30)

    Examples
    --------
    >>> from pvsolarsim.weather import OpenWeatherMapClient
    >>> from datetime import datetime
    >>> import pytz
    >>>
    >>> client = OpenWeatherMapClient(api_key='YOUR_API_KEY')
    >>> weather_data = client.read(
    ...     latitude=40.0,
    ...     longitude=-105.0,
    ...     start=datetime(2024, 1, 1, tzinfo=pytz.UTC),
    ...     end=datetime(2024, 1, 31, tzinfo=pytz.UTC)
    ... )
    """

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(
        self,
        api_key: str,
        cache_ttl: int = 86400,
        timeout: int = 30,
    ):
        self.api_key = api_key
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        self.cache = WeatherCache(ttl=cache_ttl)
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry logic.

        Returns
        -------
        requests.Session
            Configured session with automatic retries
        """
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def read(
        self,
        latitude: float,
        longitude: float,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Fetch weather data from OpenWeatherMap API.

        Parameters
        ----------
        latitude : float
            Latitude in decimal degrees (-90 to 90)
        longitude : float
            Longitude in decimal degrees (-180 to 180)
        start : datetime, optional
            Start time for data retrieval (timezone-aware)
        end : datetime, optional
            End time for data retrieval (timezone-aware)

        Returns
        -------
        pd.DataFrame
            Weather data with datetime index and standard columns

        Raises
        ------
        ValueError
            If parameters are invalid
        requests.HTTPError
            If API request fails
        """
        if start is None or end is None:
            raise ValueError("Both start and end times must be specified")

        # Check cache first
        cache_key = f"owm_{latitude}_{longitude}_{start.isoformat()}_{end.isoformat()}"
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        # Convert timestamps to Unix time
        start_ts = int(start.timestamp())
        end_ts = int(end.timestamp())

        # Fetch current weather for solar data
        # Note: OpenWeatherMap's free tier has limited historical data
        # This is a simplified implementation
        url = f"{self.BASE_URL}/onecall"
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "exclude": "minutely,alerts",
        }

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch data from OpenWeatherMap: {e}")

        # Parse response
        df = self._parse_response(data, start, end)

        # Validate data
        self.validate(df)

        # Cache the result
        self.cache.set(cache_key, df)

        return df

    def _parse_response(
        self, data: dict, start: datetime, end: datetime
    ) -> pd.DataFrame:
        """Parse OpenWeatherMap API response.

        Parameters
        ----------
        data : dict
            API response JSON
        start : datetime
            Start time for filtering
        end : datetime
            End time for filtering

        Returns
        -------
        pd.DataFrame
            Parsed weather data
        """
        # Extract hourly data
        hourly_data = data.get("hourly", [])

        records = []
        for item in hourly_data:
            timestamp = pd.to_datetime(item["dt"], unit="s", utc=True)

            # Filter by time range
            if start <= timestamp <= end:
                # OpenWeatherMap doesn't provide GHI/DNI/DHI directly
                # This is a limitation - in practice, you'd need their Solar API
                # or calculate from cloud cover
                cloud_cover = item.get("clouds", 0)

                record = {
                    "timestamp": timestamp,
                    "temp_air": item.get("temp", 25) - 273.15,  # Convert K to °C
                    "wind_speed": item.get("wind_speed", 1.0),
                    "cloud_cover": cloud_cover,
                }
                records.append(record)

        if not records:
            raise ValueError("No data available for the specified time range")

        df = pd.DataFrame(records)
        df.set_index("timestamp", inplace=True)

        return df


class PVGISClient(WeatherDataSource):
    """Client for PVGIS (Photovoltaic Geographical Information System) API.

    Fetches TMY (Typical Meteorological Year) data or historical weather data
    from the PVGIS API, which is provided by the European Commission.

    Parameters
    ----------
    cache_ttl : int, optional
        Cache time-to-live in seconds (default: 604800 = 7 days)
    timeout : int, optional
        Request timeout in seconds (default: 60)

    Examples
    --------
    >>> from pvsolarsim.weather import PVGISClient
    >>>
    >>> client = PVGISClient()
    >>> weather_data = client.read_tmy(latitude=45.0, longitude=8.0)
    """

    BASE_URL = "https://re.jrc.ec.europa.eu/api/v5_2"

    def __init__(
        self,
        cache_ttl: int = 604800,
        timeout: int = 60,
    ):
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        self.cache = WeatherCache(ttl=cache_ttl)
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry logic."""
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def read(
        self,
        latitude: float,
        longitude: float,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Fetch TMY data from PVGIS.

        Parameters
        ----------
        latitude : float
            Latitude in decimal degrees (-90 to 90)
        longitude : float
            Longitude in decimal degrees (-180 to 180)
        start : datetime, optional
            Not used for TMY data (typical year)
        end : datetime, optional
            Not used for TMY data (typical year)

        Returns
        -------
        pd.DataFrame
            Weather data with datetime index and standard columns

        Raises
        ------
        ValueError
            If parameters are invalid
        requests.HTTPError
            If API request fails
        """
        return self.read_tmy(latitude, longitude)

    def read_tmy(
        self,
        latitude: float,
        longitude: float,
    ) -> pd.DataFrame:
        """Fetch Typical Meteorological Year (TMY) data from PVGIS.

        Parameters
        ----------
        latitude : float
            Latitude in decimal degrees (-90 to 90)
        longitude : float
            Longitude in decimal degrees (-180 to 180)

        Returns
        -------
        pd.DataFrame
            TMY weather data with datetime index

        Raises
        ------
        ValueError
            If parameters are invalid
        requests.HTTPError
            If API request fails
        """
        # Check cache
        cache_key = f"pvgis_tmy_{latitude}_{longitude}"
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        # Build request URL
        url = f"{self.BASE_URL}/tmy"
        params = {
            "lat": latitude,
            "lon": longitude,
            "outputformat": "json",
        }

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch data from PVGIS: {e}")

        # Parse response
        df = self._parse_tmy_response(data)

        # Validate data
        self.validate(df)

        # Cache the result
        self.cache.set(cache_key, df)

        return df

    def _parse_tmy_response(self, data: dict) -> pd.DataFrame:
        """Parse PVGIS TMY API response.

        Parameters
        ----------
        data : dict
            API response JSON

        Returns
        -------
        pd.DataFrame
            Parsed TMY data
        """
        # Extract TMY data
        if "outputs" not in data or "tmy_hourly" not in data["outputs"]:
            raise ValueError("Invalid PVGIS response format")

        tmy_data = data["outputs"]["tmy_hourly"]

        records = []
        for item in tmy_data:
            # PVGIS provides: time, T2m, RH, G(h), Gb(n), Gd(h), IR(h), WS10m, WD10m, SP
            # G(h) = GHI, Gb(n) = DNI, Gd(h) = DHI

            # Parse timestamp (format: YYYYMMDDHHMM)
            time_str = str(item["time(UTC)"])
            timestamp = pd.to_datetime(time_str, format="%Y%m%d:%H%M", utc=True)

            record = {
                "timestamp": timestamp,
                "ghi": item.get("G(h)", 0),  # W/m²
                "dni": item.get("Gb(n)", 0),  # W/m²
                "dhi": item.get("Gd(h)", 0),  # W/m²
                "temp_air": item.get("T2m", 25),  # °C
                "wind_speed": item.get("WS10m", 1.0),  # m/s
            }
            records.append(record)

        df = pd.DataFrame(records)
        df.set_index("timestamp", inplace=True)

        return df
