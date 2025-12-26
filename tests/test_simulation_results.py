"""Tests for simulation results and statistics."""

import pandas as pd
import pytest

from pvsolarsim import Location, PVSystem
from pvsolarsim.simulation.results import AnnualStatistics, SimulationResult


class TestAnnualStatistics:
    """Test suite for AnnualStatistics dataclass."""

    def test_statistics_creation(self):
        """Test creating AnnualStatistics."""
        monthly = pd.Series([100.0] * 12, index=pd.period_range("2025-01", periods=12, freq="M"))
        daily = pd.Series([10.0] * 365, index=pd.period_range("2025-01-01", periods=365, freq="D"))

        stats = AnnualStatistics(
            total_energy_kwh=1200.0,
            capacity_factor=0.18,
            peak_power_w=3000.0,
            average_power_w=500.0,
            total_daylight_hours=4380.0,
            performance_ratio=0.85,
            monthly_energy_kwh=monthly,
            daily_energy_kwh=daily,
        )

        assert stats.total_energy_kwh == 1200.0
        assert stats.capacity_factor == 0.18
        assert stats.peak_power_w == 3000.0
        assert len(stats.monthly_energy_kwh) == 12
        assert len(stats.daily_energy_kwh) == 365

    def test_statistics_attributes(self):
        """Test all statistics attributes are accessible."""
        monthly = pd.Series([100.0] * 12, index=pd.period_range("2025-01", periods=12, freq="M"))
        daily = pd.Series([10.0] * 365, index=pd.period_range("2025-01-01", periods=365, freq="D"))

        stats = AnnualStatistics(
            total_energy_kwh=1500.0,
            capacity_factor=0.20,
            peak_power_w=3500.0,
            average_power_w=600.0,
            total_daylight_hours=4500.0,
            performance_ratio=0.90,
            monthly_energy_kwh=monthly,
            daily_energy_kwh=daily,
        )

        assert hasattr(stats, "total_energy_kwh")
        assert hasattr(stats, "capacity_factor")
        assert hasattr(stats, "peak_power_w")
        assert hasattr(stats, "average_power_w")
        assert hasattr(stats, "total_daylight_hours")
        assert hasattr(stats, "performance_ratio")
        assert hasattr(stats, "monthly_energy_kwh")
        assert hasattr(stats, "daily_energy_kwh")


class TestSimulationResult:
    """Test suite for SimulationResult dataclass."""

    @pytest.fixture
    def sample_result(self):
        """Create a sample simulation result for testing."""
        # Create time series
        times = pd.date_range("2025-01-01", periods=24, freq="H", tz="UTC")
        df = pd.DataFrame(
            {
                "power_w": [0, 0, 0, 100, 500, 1000, 1500, 2000, 2500, 3000, 2800, 2600,
                            2400, 2200, 2000, 1500, 1000, 500, 100, 0, 0, 0, 0, 0],
                "poa_irradiance": [0, 0, 0, 100, 400, 700, 900, 1000, 1100, 1200, 1150, 1100,
                                    1000, 900, 800, 600, 400, 200, 50, 0, 0, 0, 0, 0],
                "cell_temperature": [15] * 24,
            },
            index=times,
        )

        # Create statistics
        monthly = pd.Series([300.0] * 12, index=pd.period_range("2025-01", periods=12, freq="M"))
        daily = pd.Series([10.0] * 365, index=pd.period_range("2025-01-01", periods=365, freq="D"))

        stats = AnnualStatistics(
            total_energy_kwh=3600.0,
            capacity_factor=0.18,
            peak_power_w=3000.0,
            average_power_w=1200.0,
            total_daylight_hours=4380.0,
            performance_ratio=0.85,
            monthly_energy_kwh=monthly,
            daily_energy_kwh=daily,
        )

        location = Location(latitude=40.0, longitude=-105.0, altitude=1655)
        system = PVSystem(panel_area=20.0, panel_efficiency=0.20, tilt=35, azimuth=180)

        return SimulationResult(
            time_series=df,
            statistics=stats,
            location=location,
            system=system,
            interval_minutes=60,
        )

    def test_result_creation(self, sample_result):
        """Test creating SimulationResult."""
        assert isinstance(sample_result.time_series, pd.DataFrame)
        assert isinstance(sample_result.statistics, AnnualStatistics)
        assert isinstance(sample_result.location, Location)
        assert isinstance(sample_result.system, PVSystem)
        assert sample_result.interval_minutes == 60

    def test_export_csv(self, sample_result, tmp_path):
        """Test exporting time series to CSV."""
        filepath = tmp_path / "test_export.csv"
        sample_result.export_csv(str(filepath))

        assert filepath.exists()

        # Read back and verify
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        assert len(df) == len(sample_result.time_series)
        assert "power_w" in df.columns

    def test_get_monthly_summary(self, sample_result):
        """Test getting monthly summary."""
        monthly = sample_result.get_monthly_summary()

        assert isinstance(monthly, pd.DataFrame)
        assert "energy_kwh" in monthly.columns
        assert "avg_power_w" in monthly.columns
        assert "peak_power_w" in monthly.columns

    def test_get_daily_summary(self, sample_result):
        """Test getting daily summary."""
        daily = sample_result.get_daily_summary()

        assert isinstance(daily, pd.DataFrame)
        assert "energy_kwh" in daily.columns
        assert "avg_power_w" in daily.columns
        assert "peak_power_w" in daily.columns

    def test_time_series_attributes(self, sample_result):
        """Test time series has expected columns."""
        df = sample_result.time_series

        assert "power_w" in df.columns
        assert "poa_irradiance" in df.columns
        assert len(df) == 24

    def test_statistics_accessible(self, sample_result):
        """Test statistics are accessible from result."""
        assert sample_result.statistics.total_energy_kwh == 3600.0
        assert sample_result.statistics.capacity_factor == 0.18
        assert sample_result.statistics.peak_power_w == 3000.0
