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
        # Check for datetime index
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Weather data must have a DatetimeIndex")

        if data.index.tz is None:
            raise ValueError("Weather data timestamps must be timezone-aware")

        # Check required columns
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

        # Validate value ranges
        if "ghi" in data.columns:
            if (data["ghi"] < 0).any() or (data["ghi"] > 1500).any():
                raise ValueError("GHI values must be between 0 and 1500 W/m²")

        if "dni" in data.columns:
            if (data["dni"] < 0).any() or (data["dni"] > 1500).any():
                raise ValueError("DNI values must be between 0 and 1500 W/m²")

        if "dhi" in data.columns:
            if (data["dhi"] < 0).any() or (data["dhi"] > 1000).any():
                raise ValueError("DHI values must be between 0 and 1000 W/m²")

        if "temp_air" in data.columns:
            if (data["temp_air"] < -60).any() or (data["temp_air"] > 60).any():
                raise ValueError("Air temperature must be between -60 and 60 °C")

        if "wind_speed" in data.columns:
            if (data["wind_speed"] < 0).any() or (data["wind_speed"] > 50).any():
                raise ValueError("Wind speed must be between 0 and 50 m/s")

        if "cloud_cover" in data.columns:
            if (data["cloud_cover"] < 0).any() or (data["cloud_cover"] > 100).any():
                raise ValueError("Cloud cover must be between 0 and 100%")
