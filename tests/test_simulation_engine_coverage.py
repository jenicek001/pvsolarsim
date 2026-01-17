"""Additional tests for simulation engine to improve coverage.

These are quick tests that don't run full annual simulations.
"""

from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest
import pytz

from pvsolarsim import Location
from pvsolarsim.simulation.engine import _load_weather_data
from pvsolarsim.weather import CSVWeatherReader


class TestLoadWeatherData:
    """Test suite for _load_weather_data helper function."""

    @pytest.fixture
    def sample_location(self):
        """Create a sample location."""
        return Location(latitude=40.0, longitude=-105.0, altitude=1655, timezone="America/Denver")

    def test_load_weather_csv_with_file_path(self, sample_location, tmp_path):
        """Test loading weather data from CSV file using file_path kwarg."""
        # Create a simple CSV file
        csv_file = tmp_path / "weather.csv"
        timestamps = pd.date_range("2025-01-01", periods=24, freq="h", tz="UTC")
        weather_data = pd.DataFrame({
            "timestamp": timestamps,
            "ghi": [0, 0, 0, 100, 300, 500, 700, 800, 900, 950, 1000, 1000,
                    1000, 950, 900, 800, 700, 500, 300, 100, 0, 0, 0, 0],
            "temp_air": [15, 14, 13, 14, 16, 18, 20, 22, 24, 26, 28, 29,
                         30, 29, 28, 26, 24, 22, 20, 18, 16, 15, 14, 14],
            "wind_speed": [2] * 24,
        })
        weather_data.to_csv(csv_file, index=False)

        # Load weather data
        start = pytz.UTC.localize(datetime(2025, 1, 1, 0, 0))
        end = pytz.UTC.localize(datetime(2025, 1, 1, 23, 59))

        df = _load_weather_data(
            weather_source="csv",
            weather_data=None,
            location=sample_location,
            start=start,
            end=end,
            file_path=str(csv_file),
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "ghi" in df.columns
        assert "temp_air" in df.columns

    def test_load_weather_csv_with_filepath(self, sample_location, tmp_path):
        """Test loading weather data from CSV file using filepath kwarg (alternative name)."""
        # Create a simple CSV file
        csv_file = tmp_path / "weather.csv"
        timestamps = pd.date_range("2025-01-01", periods=24, freq="h", tz="UTC")
        weather_data = pd.DataFrame({
            "timestamp": timestamps,
            "ghi": [500] * 24,
            "temp_air": [25] * 24,
            "wind_speed": [3] * 24,
        })
        weather_data.to_csv(csv_file, index=False)

        # Load weather data using filepath instead of file_path
        start = pytz.UTC.localize(datetime(2025, 1, 1, 0, 0))
        end = pytz.UTC.localize(datetime(2025, 1, 1, 23, 59))

        df = _load_weather_data(
            weather_source="csv",
            weather_data=None,
            location=sample_location,
            start=start,
            end=end,
            filepath=str(csv_file),
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_load_weather_csv_missing_file_path(self, sample_location):
        """Test that missing file_path raises error for CSV source."""
        start = pytz.UTC.localize(datetime(2025, 1, 1, 0, 0))
        end = pytz.UTC.localize(datetime(2025, 1, 1, 23, 59))

        with pytest.raises(ValueError, match="file_path must be provided"):
            _load_weather_data(
                weather_source="csv",
                weather_data=None,
                location=sample_location,
                start=start,
                end=end,
            )

    def test_load_weather_custom_column_mapping(self, sample_location, tmp_path):
        """Test loading CSV with custom column mapping."""
        # Create CSV with different column names
        csv_file = tmp_path / "weather_custom.csv"
        timestamps = pd.date_range("2025-01-01", periods=24, freq="h", tz="UTC")
        weather_data = pd.DataFrame({
            "time": timestamps,
            "irradiance": [500] * 24,
            "temperature": [25] * 24,
            "wind": [3] * 24,
        })
        weather_data.to_csv(csv_file, index=False)

        start = pytz.UTC.localize(datetime(2025, 1, 1, 0, 0))
        end = pytz.UTC.localize(datetime(2025, 1, 1, 23, 59))

        df = _load_weather_data(
            weather_source="csv",
            weather_data=None,
            location=sample_location,
            start=start,
            end=end,
            file_path=str(csv_file),
            column_mapping={
                "ghi": "irradiance",
                "temp_air": "temperature",
                "wind_speed": "wind",
            },
            timestamp_column="time",
        )

        assert isinstance(df, pd.DataFrame)
        assert "ghi" in df.columns
        assert "temp_air" in df.columns
        assert "wind_speed" in df.columns

    def test_load_weather_data_source_instance(self, sample_location, tmp_path):
        """Test loading weather data from WeatherDataSource instance."""
        # Create CSV file
        csv_file = tmp_path / "weather.csv"
        timestamps = pd.date_range("2025-01-01", periods=24, freq="h", tz="UTC")
        weather_data_df = pd.DataFrame({
            "timestamp": timestamps,
            "ghi": [500] * 24,
            "temp_air": [25] * 24,
        })
        weather_data_df.to_csv(csv_file, index=False)

        # Create a WeatherDataSource instance
        reader = CSVWeatherReader(filepath=str(csv_file))

        start = pytz.UTC.localize(datetime(2025, 1, 1, 0, 0))
        end = pytz.UTC.localize(datetime(2025, 1, 1, 23, 59))

        df = _load_weather_data(
            weather_source="weather_data",
            weather_data=reader,
            location=sample_location,
            start=start,
            end=end,
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_load_weather_dataframe_directly(self, sample_location):
        """Test loading weather data from DataFrame directly."""
        # Create DataFrame
        timestamps = pd.date_range("2025-01-01", periods=24, freq="h", tz="UTC")
        weather_df = pd.DataFrame({
            "ghi": [500] * 24,
            "temp_air": [25] * 24,
            "wind_speed": [3] * 24,
        }, index=timestamps)

        start = pytz.UTC.localize(datetime(2025, 1, 1, 0, 0))
        end = pytz.UTC.localize(datetime(2025, 1, 1, 23, 59))

        df = _load_weather_data(
            weather_source="weather_data",
            weather_data=weather_df,
            location=sample_location,
            start=start,
            end=end,
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        pd.testing.assert_frame_equal(df, weather_df)

    def test_load_weather_data_missing_dataframe(self, sample_location):
        """Test that weather_data source requires data to be provided."""
        start = pytz.UTC.localize(datetime(2025, 1, 1, 0, 0))
        end = pytz.UTC.localize(datetime(2025, 1, 1, 23, 59))

        with pytest.raises(ValueError, match="weather_data must be provided"):
            _load_weather_data(
                weather_source="weather_data",
                weather_data=None,
                location=sample_location,
                start=start,
                end=end,
            )

    def test_load_weather_openweathermap_missing_api_key(self, sample_location):
        """Test that OpenWeatherMap source requires api_key."""
        start = pytz.UTC.localize(datetime(2025, 1, 1, 0, 0))
        end = pytz.UTC.localize(datetime(2025, 1, 1, 23, 59))

        with pytest.raises(ValueError, match="api_key must be provided"):
            _load_weather_data(
                weather_source="openweathermap",
                weather_data=None,
                location=sample_location,
                start=start,
                end=end,
            )

    def test_load_weather_invalid_source(self, sample_location):
        """Test that invalid weather source raises error."""
        start = pytz.UTC.localize(datetime(2025, 1, 1, 0, 0))
        end = pytz.UTC.localize(datetime(2025, 1, 1, 23, 59))

        with pytest.raises(ValueError, match="Unknown weather_source"):
            _load_weather_data(
                weather_source="invalid_source",
                weather_data=None,
                location=sample_location,
                start=start,
                end=end,
            )

    @patch('pvsolarsim.weather.api_clients.PVGISClient.read_tmy')
    def test_load_weather_pvgis(self, mock_read_tmy, sample_location):
        """Test loading weather data from PVGIS."""
        # Mock the PVGIS response
        timestamps = pd.date_range("2025-01-01", periods=24, freq="h", tz="UTC")
        mock_df = pd.DataFrame({
            "ghi": [500] * 24,
            "dni": [700] * 24,
            "dhi": [100] * 24,
            "temp_air": [25] * 24,
            "wind_speed": [3] * 24,
        }, index=timestamps)
        mock_read_tmy.return_value = mock_df

        start = pytz.UTC.localize(datetime(2025, 1, 1, 0, 0))
        end = pytz.UTC.localize(datetime(2025, 1, 1, 23, 59))

        df = _load_weather_data(
            weather_source="pvgis",
            weather_data=None,
            location=sample_location,
            start=start,
            end=end,
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 24
        mock_read_tmy.assert_called_once_with(
            latitude=sample_location.latitude,
            longitude=sample_location.longitude,
        )

    @patch('pvsolarsim.weather.api_clients.PVGISClient.read_tmy')
    def test_load_weather_pvgis_custom_parameters(self, mock_read_tmy, sample_location):
        """Test loading weather data from PVGIS with custom parameters."""
        timestamps = pd.date_range("2025-01-01", periods=24, freq="h", tz="UTC")
        mock_df = pd.DataFrame({
            "ghi": [500] * 24,
            "temp_air": [25] * 24,
        }, index=timestamps)
        mock_read_tmy.return_value = mock_df

        start = pytz.UTC.localize(datetime(2025, 1, 1, 0, 0))
        end = pytz.UTC.localize(datetime(2025, 1, 1, 23, 59))

        df = _load_weather_data(
            weather_source="pvgis",
            weather_data=None,
            location=sample_location,
            start=start,
            end=end,
            cache_ttl=3600,
            timeout=120,
        )

        assert isinstance(df, pd.DataFrame)
        mock_read_tmy.assert_called_once()

    @patch('pvsolarsim.weather.api_clients.OpenWeatherMapClient.read')
    def test_load_weather_openweathermap_with_api_key(self, mock_read, sample_location):
        """Test loading weather data from OpenWeatherMap with API key."""
        # Mock the OpenWeatherMap response
        timestamps = pd.date_range("2025-01-01", periods=24, freq="h", tz="UTC")
        mock_df = pd.DataFrame({
            "temp_air": [25] * 24,
            "wind_speed": [3] * 24,
            "cloud_cover": [20] * 24,
        }, index=timestamps)
        mock_read.return_value = mock_df

        start = pytz.UTC.localize(datetime(2025, 1, 1, 0, 0))
        end = pytz.UTC.localize(datetime(2025, 1, 1, 23, 59))

        df = _load_weather_data(
            weather_source="openweathermap",
            weather_data=None,
            location=sample_location,
            start=start,
            end=end,
            api_key="test_api_key_123",
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 24
        mock_read.assert_called_once_with(
            latitude=sample_location.latitude,
            longitude=sample_location.longitude,
            start=start,
            end=end,
        )

    @patch('pvsolarsim.weather.api_clients.OpenWeatherMapClient.read')
    def test_load_weather_openweathermap_custom_parameters(self, mock_read, sample_location):
        """Test loading weather data from OpenWeatherMap with custom cache/timeout."""
        timestamps = pd.date_range("2025-01-01", periods=24, freq="h", tz="UTC")
        mock_df = pd.DataFrame({
            "temp_air": [25] * 24,
            "wind_speed": [3] * 24,
        }, index=timestamps)
        mock_read.return_value = mock_df

        start = pytz.UTC.localize(datetime(2025, 1, 1, 0, 0))
        end = pytz.UTC.localize(datetime(2025, 1, 1, 23, 59))

        df = _load_weather_data(
            weather_source="openweathermap",
            weather_data=None,
            location=sample_location,
            start=start,
            end=end,
            api_key="test_key",
            cache_ttl=7200,
            timeout=60,
        )

        assert isinstance(df, pd.DataFrame)
        mock_read.assert_called_once()

