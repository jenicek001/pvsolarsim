"""Base classes for weather data sources.

This module defines the abstract interface for all weather data sources
in PVSolarSim.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

import pandas as pd


class WeatherDataSource(ABC):
    """Abstract base class for weather data sources.

    All weather data sources must implement this interface to ensure
    consistent data format and behavior.

    The standard weather data format is a pandas DataFrame with the following columns:
    - timestamp: datetime index (timezone-aware)
    - ghi: Global Horizontal Irradiance (W/m²)
    - dni: Direct Normal Irradiance (W/m²) [optional]
    - dhi: Diffuse Horizontal Irradiance (W/m²) [optional]
    - temp_air: Ambient air temperature (°C)
    - wind_speed: Wind speed (m/s) [optional]
    - cloud_cover: Cloud cover (0-100%) [optional]
    """

    @abstractmethod
    def read(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Read weather data for the specified time range.

        Parameters
        ----------
        start : datetime, optional
            Start time for data retrieval (timezone-aware)
        end : datetime, optional
            End time for data retrieval (timezone-aware)

        Returns
        -------
        pd.DataFrame
            Weather data with datetime index and required columns

        Raises
        ------
        ValueError
            If data validation fails or required columns are missing
        """
        pass

    def validate(self, data: pd.DataFrame) -> None:
        """Validate weather data format and value ranges.

        Parameters
        ----------
        data : pd.DataFrame
            Weather data to validate

        Raises
        ------
        ValueError
            If validation fails
        """
        self._validate_index(data)
        self._validate_required_columns(data)
        self._validate_value_ranges(data)

    def _validate_index(self, data: pd.DataFrame) -> None:
        """Validate DataFrame index is timezone-aware DatetimeIndex."""
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Weather data must have a DatetimeIndex")

        if data.index.tz is None:
            raise ValueError("Weather data timestamps must be timezone-aware")

    def _validate_required_columns(self, data: pd.DataFrame) -> None:
        """Validate required columns are present."""
        required_columns = ["temp_air"]
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # At least one irradiance component must be present
        irradiance_columns = ["ghi", "dni", "dhi"]
        has_irradiance = any(col in data.columns for col in irradiance_columns)
        if not has_irradiance:
            raise ValueError(
                "Weather data must contain at least one irradiance column (ghi, dni, or dhi)"
            )

    def _validate_value_ranges(self, data: pd.DataFrame) -> None:
        """Validate all values are within acceptable ranges."""
        # Define validation rules: (column_name, min, max, unit, error_msg_prefix)
        validations = [
            ("ghi", 0, 1500, "W/m²", "GHI values"),
            ("dni", 0, 1500, "W/m²", "DNI values"),
            ("dhi", 0, 1000, "W/m²", "DHI values"),
            ("temp_air", -60, 60, "°C", "Air temperature"),
            ("wind_speed", 0, 50, "m/s", "Wind speed"),
            ("cloud_cover", 0, 100, "%", "Cloud cover"),
        ]

        for col_name, min_val, max_val, unit, msg_prefix in validations:
            if col_name in data.columns:
                self._validate_column_range(data[col_name], msg_prefix, min_val, max_val, unit)

    def _validate_column_range(
        self, series: pd.Series, msg_prefix: str, min_val: float, max_val: float, unit: str
    ) -> None:
        """Validate a column is within specified range."""
        if (series < min_val).any() or (series > max_val).any():
            raise ValueError(f"{msg_prefix} must be between {min_val} and {max_val} {unit}")
