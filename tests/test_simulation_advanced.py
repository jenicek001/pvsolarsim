"""Advanced tests for simulation engine with high coverage.

These tests focus on testing individual functions and edge cases
without running full slow annual simulations.
"""

from datetime import datetime

import pandas as pd
import pytest
import pytz

from pvsolarsim import Location, PVSystem
from pvsolarsim.simulation.engine import (
    _calculate_statistics,
    _load_weather_data,
    simulate_annual,
)
from pvsolarsim.simulation.results import AnnualStatistics


class TestLoadWeatherData:
    """Test weather data loading from various sources."""

    @pytest.fixture
    def sample_location(self):
        """Create a sample location."""
        return Location(latitude=40.0, longitude=-105.0, altitude=1655, timezone="America/Denver")

    @pytest.fixture
    def sample_weather_data(self):
        """Create sample weather DataFrame."""
        times = pd.date_range("2025-01-01", periods=24, freq="h", tz="UTC")
        return pd.DataFrame(
            {
                "ghi": [0, 0, 0, 0, 0, 100, 300, 500, 700, 800, 900, 950] * 2,
                "dni": [0, 0, 0, 0, 0, 200, 400, 600, 800, 900, 950, 1000] * 2,
                "dhi": [0, 0, 0, 0, 0, 50, 100, 150, 150, 150, 150, 150] * 2,
                "temp_air": [10, 9, 8, 8, 9, 12, 15, 18, 21, 24, 26, 27] * 2,
                "wind_speed": [2, 2, 2, 2, 3, 3, 3, 4, 4, 4, 3, 3] * 2,
                "cloud_cover": [0, 0, 0, 0, 10, 10, 20, 20, 10, 0, 0, 0] * 2,
            },
            index=times,
        )

    def test_load_weather_data_dataframe(self, sample_location, sample_weather_data):
        """Test loading weather data from DataFrame."""
        start = pytz.UTC.localize(datetime(2025, 1, 1))
        end = pytz.UTC.localize(datetime(2025, 1, 2))

        result = _load_weather_data(
            weather_source="weather_data",
            weather_data=sample_weather_data,
            location=sample_location,
            start=start,
            end=end,
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert "ghi" in result.columns

    def test_load_weather_data_missing_dataframe(self, sample_location):
        """Test error when DataFrame is missing."""
        start = pytz.UTC.localize(datetime(2025, 1, 1))
        end = pytz.UTC.localize(datetime(2025, 1, 2))

        with pytest.raises(ValueError, match="weather_data must be provided"):
            _load_weather_data(
                weather_source="weather_data",
                weather_data=None,
                location=sample_location,
                start=start,
                end=end,
            )

    def test_load_weather_data_csv(self, sample_location, sample_weather_data, tmp_path):
        """Test loading weather data from CSV file."""
        # Create temporary CSV file
        csv_file = tmp_path / "weather.csv"
        # Reset index to include timestamp column
        sample_weather_data.reset_index().to_csv(csv_file, index=False)

        start = pytz.UTC.localize(datetime(2025, 1, 1))
        end = pytz.UTC.localize(datetime(2025, 1, 2))

        result = _load_weather_data(
            weather_source="csv",
            weather_data=None,
            location=sample_location,
            start=start,
            end=end,
            file_path=str(csv_file),
            timestamp_column="index",  # Use 'index' as the timestamp column name
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_load_weather_data_csv_missing_path(self, sample_location):
        """Test error when CSV path is missing."""
        start = pytz.UTC.localize(datetime(2025, 1, 1))
        end = pytz.UTC.localize(datetime(2025, 1, 2))

        with pytest.raises(ValueError, match="file_path must be provided"):
            _load_weather_data(
                weather_source="csv",
                weather_data=None,
                location=sample_location,
                start=start,
                end=end,
            )

    def test_load_weather_data_openweathermap_missing_key(self, sample_location):
        """Test error when OpenWeatherMap API key is missing."""
        start = pytz.UTC.localize(datetime(2025, 1, 1))
        end = pytz.UTC.localize(datetime(2025, 1, 2))

        with pytest.raises(ValueError, match="api_key must be provided"):
            _load_weather_data(
                weather_source="openweathermap",
                weather_data=None,
                location=sample_location,
                start=start,
                end=end,
            )

    def test_load_weather_data_invalid_source(self, sample_location):
        """Test error when weather source is invalid."""
        start = pytz.UTC.localize(datetime(2025, 1, 1))
        end = pytz.UTC.localize(datetime(2025, 1, 2))

        with pytest.raises(ValueError, match="Unknown weather_source"):
            _load_weather_data(
                weather_source="invalid_source",
                weather_data=None,
                location=sample_location,
                start=start,
                end=end,
            )


class TestCalculateStatistics:
    """Test statistics calculation function."""

    @pytest.fixture
    def sample_system(self):
        """Create a sample PV system."""
        return PVSystem(
            panel_area=20.0,
            panel_efficiency=0.20,
            tilt=35.0,
            azimuth=180.0,
            temp_coefficient=-0.004,
        )

    @pytest.fixture
    def sample_time_series(self):
        """Create sample time series data."""
        times = pd.date_range("2025-06-21", periods=24, freq="h", tz="UTC")
        return pd.DataFrame(
            {
                "power_w": [0, 0, 0, 0, 100, 500, 1000, 2000, 3000, 3500, 3800, 3900,
                           3800, 3500, 3000, 2000, 1000, 500, 100, 0, 0, 0, 0, 0],
                "poa_irradiance": [0, 0, 0, 0, 50, 250, 500, 800, 950, 1000, 1050, 1100,
                                  1050, 1000, 950, 800, 500, 250, 50, 0, 0, 0, 0, 0],
                "solar_elevation": [-30.0, -25.0, -20.0, -10.0, 5.0, 15.0, 30.0, 45.0, 60.0, 70.0, 75.0, 73.0,
                                   70.0, 60.0, 45.0, 30.0, 15.0, 5.0, -10.0, -20.0, -25.0, -30.0, -35.0, -40.0],
                "cell_temperature": [10.0, 10.0, 10.0, 10.0, 15.0, 20.0, 30.0, 40.0, 50.0, 55.0, 58.0, 60.0,
                                    58.0, 55.0, 50.0, 40.0, 30.0, 20.0, 15.0, 10.0, 10.0, 10.0, 10.0, 10.0],
            },
            index=times,
        )

    def test_calculate_statistics_basic(self, sample_time_series, sample_system):
        """Test basic statistics calculation."""
        stats = _calculate_statistics(sample_time_series, sample_system, interval_minutes=60)

        assert isinstance(stats, AnnualStatistics)
        assert stats.total_energy_kwh > 0
        assert stats.peak_power_w > 0
        assert stats.average_power_w >= 0
        assert stats.capacity_factor >= 0
        assert stats.performance_ratio >= 0

    def test_calculate_statistics_total_energy(self, sample_time_series, sample_system):
        """Test total energy calculation."""
        stats = _calculate_statistics(sample_time_series, sample_system, interval_minutes=60)

        # Energy = sum(power * time_interval)
        # For 1 hour interval: sum(power_w) / 1000 (to get kWh)
        expected_energy = sample_time_series["power_w"].sum() / 1000.0
        assert abs(stats.total_energy_kwh - expected_energy) < 0.01

    def test_calculate_statistics_peak_power(self, sample_time_series, sample_system):
        """Test peak power calculation."""
        stats = _calculate_statistics(sample_time_series, sample_system, interval_minutes=60)

        expected_peak = sample_time_series["power_w"].max()
        assert stats.peak_power_w == expected_peak

    def test_calculate_statistics_daylight_hours(self, sample_time_series, sample_system):
        """Test daylight hours calculation."""
        stats = _calculate_statistics(sample_time_series, sample_system, interval_minutes=60)

        # Count hours where solar elevation > 0
        daylight_count = (sample_time_series["solar_elevation"] > 0).sum()
        expected_hours = daylight_count * 1.0  # 1 hour interval

        assert abs(stats.total_daylight_hours - expected_hours) < 0.01

    def test_calculate_statistics_capacity_factor(self, sample_time_series, sample_system):
        """Test capacity factor calculation."""
        stats = _calculate_statistics(sample_time_series, sample_system, interval_minutes=60)

        # CF = Actual Energy / (Rated Power * 8760)
        rated_power_w = sample_system.panel_area * sample_system.panel_efficiency * 1000
        expected_cf = stats.total_energy_kwh / (rated_power_w * 8760 / 1000.0)

        assert abs(stats.capacity_factor - expected_cf) < 0.001

    def test_calculate_statistics_different_intervals(self, sample_time_series, sample_system):
        """Test statistics with different time intervals."""
        stats_60 = _calculate_statistics(sample_time_series, sample_system, interval_minutes=60)
        stats_30 = _calculate_statistics(sample_time_series, sample_system, interval_minutes=30)

        # With 30-minute intervals, energy should be half
        assert abs(stats_30.total_energy_kwh - stats_60.total_energy_kwh / 2) < 0.1

    def test_calculate_statistics_zero_power(self, sample_system):
        """Test statistics with all zero power."""
        times = pd.date_range("2025-01-01", periods=24, freq="h", tz="UTC")
        df = pd.DataFrame(
            {
                "power_w": [0.0] * 24,
                "poa_irradiance": [0.0] * 24,
                "solar_elevation": [-10.0] * 24,
                "cell_temperature": [10.0] * 24,
            },
            index=times,
        )

        stats = _calculate_statistics(df, sample_system, interval_minutes=60)

        assert stats.total_energy_kwh == 0
        assert stats.peak_power_w == 0
        assert stats.average_power_w == 0


class TestSimulateAnnualValidation:
    """Test simulate_annual parameter validation (fast tests only)."""

    @pytest.fixture
    def sample_location(self):
        """Create a sample location."""
        return Location(latitude=40.0, longitude=-105.0, altitude=1655, timezone="America/Denver")

    @pytest.fixture
    def sample_system(self):
        """Create a sample PV system."""
        return PVSystem(
            panel_area=20.0,
            panel_efficiency=0.20,
            tilt=35.0,
            azimuth=180.0,
            temp_coefficient=-0.004,
        )

    def test_simulate_annual_invalid_interval_too_low(self, sample_location, sample_system):
        """Test error with interval < 1."""
        with pytest.raises(ValueError, match="interval_minutes must be between 1 and 60"):
            simulate_annual(
                location=sample_location,
                system=sample_system,
                year=2025,
                interval_minutes=0,
            )

    def test_simulate_annual_invalid_interval_too_high(self, sample_location, sample_system):
        """Test error with interval > 60."""
        with pytest.raises(ValueError, match="interval_minutes must be between 1 and 60"):
            simulate_annual(
                location=sample_location,
                system=sample_system,
                year=2025,
                interval_minutes=61,
            )

    def test_simulate_annual_weather_source_validation(self, sample_location, sample_system):
        """Test error with invalid weather source."""
        with pytest.raises(ValueError, match="Unknown weather_source"):
            # Use _load_weather_data directly to avoid slow simulation
            start = pytz.UTC.localize(datetime(2025, 1, 1))
            end = pytz.UTC.localize(datetime(2025, 1, 2))
            _load_weather_data(
                weather_source="invalid_source",
                weather_data=None,
                location=sample_location,
                start=start,
                end=end,
            )
