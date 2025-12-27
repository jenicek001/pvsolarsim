"""Tests for weather data base classes and validation."""

import pandas as pd
import pytest

from pvsolarsim.weather.base import WeatherDataSource


class MockWeatherDataSource(WeatherDataSource):
    """Mock weather data source for testing."""

    def __init__(self, data: pd.DataFrame):
        self.data = data

    def read(self, start=None, end=None):
        return self.data


def test_validate_valid_data():
    """Test validation with valid weather data."""
    timestamps = pd.date_range("2025-01-01", periods=24, freq="H", tz="UTC")
    data = pd.DataFrame(
        {
            "ghi": [100.0] * 24,
            "dni": [200.0] * 24,
            "dhi": [50.0] * 24,
            "temp_air": [25.0] * 24,
            "wind_speed": [3.0] * 24,
            "cloud_cover": [20.0] * 24,
        },
        index=timestamps,
    )

    source = MockWeatherDataSource(data)
    # Should not raise
    source.validate(data)


def test_validate_missing_timezone():
    """Test validation fails with naive datetime index."""
    timestamps = pd.date_range("2025-01-01", periods=24, freq="H")  # No timezone
    data = pd.DataFrame(
        {
            "ghi": [100.0] * 24,
            "temp_air": [25.0] * 24,
        },
        index=timestamps,
    )

    source = MockWeatherDataSource(data)
    with pytest.raises(ValueError, match="timezone-aware"):
        source.validate(data)


def test_validate_missing_required_column():
    """Test validation fails when required column is missing."""
    timestamps = pd.date_range("2025-01-01", periods=24, freq="H", tz="UTC")
    data = pd.DataFrame(
        {
            "ghi": [100.0] * 24,
            # Missing temp_air
        },
        index=timestamps,
    )

    source = MockWeatherDataSource(data)
    with pytest.raises(ValueError, match="Missing required columns"):
        source.validate(data)


def test_validate_no_irradiance():
    """Test validation fails when no irradiance columns present."""
    timestamps = pd.date_range("2025-01-01", periods=24, freq="H", tz="UTC")
    data = pd.DataFrame(
        {
            "temp_air": [25.0] * 24,
            # No GHI, DNI, or DHI
        },
        index=timestamps,
    )

    source = MockWeatherDataSource(data)
    with pytest.raises(ValueError, match="at least one irradiance column"):
        source.validate(data)


def test_validate_ghi_out_of_range():
    """Test validation fails with GHI out of valid range."""
    timestamps = pd.date_range("2025-01-01", periods=24, freq="H", tz="UTC")

    # Test negative GHI
    data = pd.DataFrame(
        {
            "ghi": [-10.0] * 24,
            "temp_air": [25.0] * 24,
        },
        index=timestamps,
    )
    source = MockWeatherDataSource(data)
    with pytest.raises(ValueError, match="GHI values must be between"):
        source.validate(data)

    # Test too high GHI
    data = pd.DataFrame(
        {
            "ghi": [2000.0] * 24,
            "temp_air": [25.0] * 24,
        },
        index=timestamps,
    )
    source = MockWeatherDataSource(data)
    with pytest.raises(ValueError, match="GHI values must be between"):
        source.validate(data)


def test_validate_temperature_out_of_range():
    """Test validation fails with temperature out of valid range."""
    timestamps = pd.date_range("2025-01-01", periods=24, freq="H", tz="UTC")

    # Test too cold
    data = pd.DataFrame(
        {
            "ghi": [100.0] * 24,
            "temp_air": [-70.0] * 24,
        },
        index=timestamps,
    )
    source = MockWeatherDataSource(data)
    with pytest.raises(ValueError, match="Air temperature must be between"):
        source.validate(data)

    # Test too hot
    data = pd.DataFrame(
        {
            "ghi": [100.0] * 24,
            "temp_air": [70.0] * 24,
        },
        index=timestamps,
    )
    source = MockWeatherDataSource(data)
    with pytest.raises(ValueError, match="Air temperature must be between"):
        source.validate(data)


def test_validate_wind_speed_out_of_range():
    """Test validation fails with wind speed out of valid range."""
    timestamps = pd.date_range("2025-01-01", periods=24, freq="H", tz="UTC")

    # Test negative wind
    data = pd.DataFrame(
        {
            "ghi": [100.0] * 24,
            "temp_air": [25.0] * 24,
            "wind_speed": [-1.0] * 24,
        },
        index=timestamps,
    )
    source = MockWeatherDataSource(data)
    with pytest.raises(ValueError, match="Wind speed must be between"):
        source.validate(data)


def test_validate_cloud_cover_out_of_range():
    """Test validation fails with cloud cover out of valid range."""
    timestamps = pd.date_range("2025-01-01", periods=24, freq="H", tz="UTC")

    # Test negative cloud cover
    data = pd.DataFrame(
        {
            "ghi": [100.0] * 24,
            "temp_air": [25.0] * 24,
            "cloud_cover": [-10.0] * 24,
        },
        index=timestamps,
    )
    source = MockWeatherDataSource(data)
    with pytest.raises(ValueError, match="Cloud cover must be between"):
        source.validate(data)


def test_validate_not_dataframe_index():
    """Test validation fails when index is not DatetimeIndex."""
    data = pd.DataFrame(
        {
            "ghi": [100.0] * 24,
            "temp_air": [25.0] * 24,
        }
    )

    source = MockWeatherDataSource(data)
    with pytest.raises(ValueError, match="must have a DatetimeIndex"):
        source.validate(data)
