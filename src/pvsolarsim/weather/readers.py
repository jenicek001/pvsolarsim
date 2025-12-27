"""File readers for weather data.

This module provides implementations for reading weather data from various
file formats including CSV, JSON, and EPW (EnergyPlus Weather) files.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union

import pandas as pd

from pvsolarsim.weather.base import WeatherDataSource


class CSVWeatherReader(WeatherDataSource):
    """Read weather data from CSV files.

    Supports flexible column mapping to handle different CSV formats and
    naming conventions. Missing data can be filled using various strategies.

    Parameters
    ----------
    filepath : str or Path
        Path to the CSV file
    column_mapping : dict, optional
        Mapping from standard column names to CSV column names.
        Standard names: 'timestamp', 'ghi', 'dni', 'dhi', 'temp_air',
        'wind_speed', 'cloud_cover'. If not provided, assumes CSV uses
        standard column names.
    timestamp_column : str, optional
        Name of the timestamp column (default: 'timestamp')
    timestamp_format : str, optional
        Format string for parsing timestamps (default: ISO 8601)
    timezone : str, optional
        Timezone for timestamps if not included in data (default: 'UTC')
    skip_rows : int, optional
        Number of rows to skip at the beginning (default: 0)
    delimiter : str, optional
        CSV delimiter (default: ',')

    Examples
    --------
    >>> # Simple CSV with standard column names
    >>> reader = CSVWeatherReader('weather.csv')
    >>> weather_data = reader.read()
    >>>
    >>> # CSV with custom column names
    >>> reader = CSVWeatherReader(
    ...     'custom_weather.csv',
    ...     column_mapping={
    ...         'ghi': 'global_irradiance',
    ...         'temp_air': 'temperature_c',
    ...         'wind_speed': 'wind_m_s'
    ...     },
    ...     timestamp_column='datetime',
    ...     timezone='America/Denver'
    ... )
    >>> weather_data = reader.read()
    """

    def __init__(
        self,
        filepath: Union[str, Path],
        column_mapping: Optional[Dict[str, str]] = None,
        timestamp_column: str = "timestamp",
        timestamp_format: Optional[str] = None,
        timezone: str = "UTC",
        skip_rows: int = 0,
        delimiter: str = ",",
    ):
        self.filepath = Path(filepath)
        self.column_mapping = column_mapping or {}
        self.timestamp_column = timestamp_column
        self.timestamp_format = timestamp_format
        self.timezone = timezone
        self.skip_rows = skip_rows
        self.delimiter = delimiter

        if not self.filepath.exists():
            raise FileNotFoundError(f"Weather data file not found: {filepath}")

    def read(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Read weather data from CSV file.

        Parameters
        ----------
        start : datetime, optional
            Start time for filtering data (timezone-aware)
        end : datetime, optional
            End time for filtering data (timezone-aware)

        Returns
        -------
        pd.DataFrame
            Weather data with datetime index and standardized columns

        Raises
        ------
        ValueError
            If data validation fails or required columns are missing
        FileNotFoundError
            If the CSV file does not exist
        """
        # Read CSV file
        df = pd.read_csv(
            self.filepath,
            skiprows=self.skip_rows,
            delimiter=self.delimiter,
        )

        # Parse timestamp column
        timestamp_col = self.column_mapping.get("timestamp", self.timestamp_column)

        if timestamp_col not in df.columns:
            raise ValueError(
                f"Timestamp column '{timestamp_col}' not found in CSV. "
                f"Available columns: {list(df.columns)}"
            )

        # Parse timestamps
        if self.timestamp_format:
            df["timestamp"] = pd.to_datetime(df[timestamp_col], format=self.timestamp_format)
        else:
            df["timestamp"] = pd.to_datetime(df[timestamp_col])

        # Apply timezone
        if df["timestamp"].dt.tz is None:
            df["timestamp"] = df["timestamp"].dt.tz_localize(self.timezone)
        else:
            # Convert to specified timezone
            df["timestamp"] = df["timestamp"].dt.tz_convert(self.timezone)

        # Set timestamp as index
        df.set_index("timestamp", inplace=True)

        # Apply column mapping to rename columns
        rename_dict = {}
        for standard_name, csv_name in self.column_mapping.items():
            if standard_name != "timestamp" and csv_name in df.columns:
                rename_dict[csv_name] = standard_name

        if rename_dict:
            df.rename(columns=rename_dict, inplace=True)

        # Select only relevant columns
        standard_columns = ["ghi", "dni", "dhi", "temp_air", "wind_speed", "cloud_cover"]
        available_columns = [col for col in standard_columns if col in df.columns]
        df = df[available_columns]

        # Filter by date range if specified
        if start is not None:
            # Convert start to matching timezone for comparison
            start_ts = pd.Timestamp(start).tz_convert(df.index.tz)
            df = df[df.index >= start_ts]
        if end is not None:
            # Convert end to matching timezone for comparison
            end_ts = pd.Timestamp(end).tz_convert(df.index.tz)
            df = df[df.index <= end_ts]

        # Validate data
        self.validate(df)

        return df


class JSONWeatherReader(WeatherDataSource):
    """Read weather data from JSON files.

    Parameters
    ----------
    filepath : str or Path
        Path to the JSON file
    timezone : str, optional
        Timezone for timestamps if not included in data (default: 'UTC')

    Examples
    --------
    >>> reader = JSONWeatherReader('weather.json', timezone='America/Denver')
    >>> weather_data = reader.read()
    """

    def __init__(
        self,
        filepath: Union[str, Path],
        timezone: str = "UTC",
    ):
        self.filepath = Path(filepath)
        self.timezone = timezone

        if not self.filepath.exists():
            raise FileNotFoundError(f"Weather data file not found: {filepath}")

    def read(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Read weather data from JSON file.

        The JSON file should contain an array of records with timestamp
        and weather data fields.

        Parameters
        ----------
        start : datetime, optional
            Start time for filtering data (timezone-aware)
        end : datetime, optional
            End time for filtering data (timezone-aware)

        Returns
        -------
        pd.DataFrame
            Weather data with datetime index and standardized columns

        Raises
        ------
        ValueError
            If data validation fails or required columns are missing
        FileNotFoundError
            If the JSON file does not exist
        """
        # Read JSON file
        df = pd.read_json(self.filepath)

        # Parse timestamp column
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        else:
            raise ValueError("JSON file must contain 'timestamp' field")

        # Apply timezone
        if df["timestamp"].dt.tz is None:
            df["timestamp"] = df["timestamp"].dt.tz_localize(self.timezone)
        else:
            df["timestamp"] = df["timestamp"].dt.tz_convert(self.timezone)

        # Set timestamp as index
        df.set_index("timestamp", inplace=True)

        # Select only relevant columns
        standard_columns = ["ghi", "dni", "dhi", "temp_air", "wind_speed", "cloud_cover"]
        available_columns = [col for col in standard_columns if col in df.columns]
        df = df[available_columns]

        # Filter by date range if specified
        if start is not None:
            # Convert start to matching timezone for comparison
            start_ts = pd.Timestamp(start).tz_convert(df.index.tz)
            df = df[df.index >= start_ts]
        if end is not None:
            # Convert end to matching timezone for comparison
            end_ts = pd.Timestamp(end).tz_convert(df.index.tz)
            df = df[df.index <= end_ts]

        # Validate data
        self.validate(df)

        return df
