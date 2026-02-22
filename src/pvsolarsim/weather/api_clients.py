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
        int(start.timestamp())
        int(end.timestamp())

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
            raise ValueError(f"Failed to fetch data from OpenWeatherMap: {e}") from e

        # Parse response
        df = self._parse_response(data, start, end)

        # Validate data (skip irradiance check for OpenWeatherMap free tier)
        self._validate_openweathermap_data(df)

        # Cache the result
        self.cache.set(cache_key, df)

        return df

    def _validate_openweathermap_data(self, data: pd.DataFrame) -> None:
        """Validate OpenWeatherMap data (without irradiance requirement).

        OpenWeatherMap's free tier doesn't provide GHI/DNI/DHI, so we
        only validate basic structure and temperature/wind data.
        """
        # Validate index
        self._validate_index(data)

        # Check for required columns (temp_air is mandatory)
        if "temp_air" not in data.columns:
            raise ValueError("Missing required column: temp_air")

        # Validate value ranges (only for columns that exist)
        if "temp_air" in data.columns:
            if (data["temp_air"] < -60).any() or (data["temp_air"] > 60).any():
                raise ValueError("Air temperature must be between -60 and 60 °C")

        if "wind_speed" in data.columns:
            if (data["wind_speed"] < 0).any() or (data["wind_speed"] > 50).any():
                raise ValueError("Wind speed must be between 0 and 50 m/s")

        if "cloud_cover" in data.columns:
            if (data["cloud_cover"] < 0).any() or (data["cloud_cover"] > 100).any():
                raise ValueError("Cloud cover must be between 0 and 100 %")

    def _parse_response(self, data: dict, start: datetime, end: datetime) -> pd.DataFrame:
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


class VisualCrossingClient(WeatherDataSource):
    """Client for Visual Crossing Weather API.

    Fetches historical and forecast weather data including solar radiation
    (GHI, DNI) from Visual Crossing's Timeline API. Supports global coverage
    and hourly data resolution.

    Parameters
    ----------
    api_key : str
        Visual Crossing API key (get free key at visualcrossing.com)
    cache_ttl : int, optional
        Cache time-to-live in seconds (default: 86400 = 24 hours)
    timeout : int, optional
        Request timeout in seconds (default: 60)

    Notes
    -----
    Free tier includes 1000 API calls per day, which is sufficient for
    most development and testing purposes.

    Examples
    --------
    >>> from pvsolarsim.weather import VisualCrossingClient
    >>> from datetime import datetime
    >>> import pytz
    >>>
    >>> client = VisualCrossingClient(api_key='YOUR_API_KEY')
    >>> weather_data = client.read(
    ...     latitude=40.0,
    ...     longitude=-105.0,
    ...     start=datetime(2024, 1, 1, tzinfo=pytz.UTC),
    ...     end=datetime(2024, 1, 31, tzinfo=pytz.UTC)
    ... )
    """

    BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

    def __init__(
        self,
        api_key: str,
        cache_ttl: int = 86400,
        timeout: int = 60,
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
        """Fetch historical weather data from Visual Crossing API.

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
            Weather data with datetime index and columns:
            - ghi: Global Horizontal Irradiance (W/m²)
            - dni: Direct Normal Irradiance (W/m²)
            - temp_air: Air temperature (°C)
            - wind_speed: Wind speed (m/s)
            - cloud_cover: Cloud cover percentage (0-100)

        Raises
        ------
        ValueError
            If parameters are invalid or API returns invalid data
        requests.HTTPError
            If API request fails
        """
        if start is None or end is None:
            raise ValueError("Both start and end times must be specified")

        # Validate coordinates
        if not -90 <= latitude <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
        if not -180 <= longitude <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")

        # Check cache first
        cache_key = f"vc_{latitude}_{longitude}_{start.isoformat()}_{end.isoformat()}"
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        # Format dates as YYYY-MM-DD
        start_date = start.strftime("%Y-%m-%d")
        end_date = end.strftime("%Y-%m-%d")

        # Construct URL
        location = f"{latitude},{longitude}"
        url = f"{self.BASE_URL}/{location}/{start_date}/{end_date}"

        # API parameters
        params = {
            "key": self.api_key,
            "unitGroup": "metric",  # Use metric units
            "include": "hours",  # Include hourly data
            "elements": "datetime,temp,windspeed,cloudcover,solarradiation,solarenergy,uvindex",
            "contentType": "json",
        }

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch data from Visual Crossing: {e}") from e

        # Parse response
        df = self._parse_response(data)

        # Validate data
        self.validate(df)

        # Cache the result
        self.cache.set(cache_key, df)

        return df

    def read_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 15,
    ) -> pd.DataFrame:
        """Fetch weather forecast from Visual Crossing API.

        Parameters
        ----------
        latitude : float
            Latitude in decimal degrees (-90 to 90)
        longitude : float
            Longitude in decimal degrees (-180 to 180)
        days : int, optional
            Number of forecast days (1-15, default: 15)

        Returns
        -------
        pd.DataFrame
            Forecast weather data with same format as read()

        Raises
        ------
        ValueError
            If parameters are invalid
        requests.HTTPError
            If API request fails
        """
        if not 1 <= days <= 15:
            raise ValueError(f"Forecast days must be between 1 and 15, got {days}")

        # Validate coordinates
        if not -90 <= latitude <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
        if not -180 <= longitude <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")

        # Construct URL for forecast (no date range = forecast)
        location = f"{latitude},{longitude}"
        url = f"{self.BASE_URL}/{location}"

        # API parameters
        params = {
            "key": self.api_key,
            "unitGroup": "metric",
            "include": "hours",
            "elements": "datetime,temp,windspeed,cloudcover,solarradiation,solarenergy,uvindex",
            "contentType": "json",
        }

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch forecast from Visual Crossing: {e}") from e

        # Parse response
        df = self._parse_response(data)

        # Limit to requested number of days
        if len(df) > days * 24:
            df = df.iloc[: days * 24]

        return df

    def _parse_response(self, data: dict) -> pd.DataFrame:
        """Parse Visual Crossing API response.

        Parameters
        ----------
        data : dict
            API response JSON

        Returns
        -------
        pd.DataFrame
            Parsed weather data with standardized columns
        """
        if "days" not in data:
            raise ValueError("Invalid Visual Crossing response format: missing 'days' field")

        records = []

        for day in data["days"]:
            # Process hourly data if available
            if "hours" in day:
                for hour in day["hours"]:
                    # Parse timestamp
                    # Format: "2024-01-01T12:00:00"
                    datetime_str = hour.get("datetime")
                    if datetime_str:
                        # Combine date and time
                        date_str = day.get("datetime")
                        full_datetime = f"{date_str}T{datetime_str}"
                        timestamp = pd.to_datetime(full_datetime, utc=True)
                    else:
                        continue

                    # Extract solar radiation
                    # Visual Crossing provides solarradiation in W/m² (average over the hour)
                    # This is essentially GHI
                    solar_radiation = hour.get("solarradiation", 0)

                    # Visual Crossing doesn't provide DNI directly
                    # We can estimate it from GHI and cloud cover
                    # DNI ≈ GHI / (1 - 0.75 * cloud_cover/100) for clear sky component
                    cloud_cover = hour.get("cloudcover", 0)
                    # Simplified DNI estimation (better than nothing)
                    if solar_radiation > 0 and cloud_cover < 100:
                        estimated_dni = solar_radiation * (1 + 0.5 * (100 - cloud_cover) / 100)
                    else:
                        estimated_dni = 0

                    record = {
                        "timestamp": timestamp,
                        "ghi": solar_radiation,  # W/m²
                        "dni": estimated_dni,  # W/m² (estimated)
                        "dhi": max(0, solar_radiation * 0.3),  # Rough estimate: 30% diffuse
                        "temp_air": hour.get("temp", 25),  # °C
                        "wind_speed": hour.get("windspeed", 1.0) / 3.6,  # Convert km/h to m/s
                        "cloud_cover": cloud_cover,  # %
                    }
                    records.append(record)

        if not records:
            raise ValueError("No hourly data available in Visual Crossing response")

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
            raise ValueError(f"Failed to fetch data from PVGIS: {e}") from e

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
