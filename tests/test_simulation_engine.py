"""Tests for simulation engine."""

import pandas as pd
import pytest

from pvsolarsim import Location, PVSystem
from pvsolarsim.simulation import SimulationResult, simulate_annual


class TestSimulateAnnual:
    """Test suite for annual simulation."""

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

    def test_basic_annual_simulation(self, sample_location, sample_system):
        """Test basic annual simulation with clear sky."""
        result = simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2025,
            interval_minutes=60,  # Hourly for speed
        )

        assert isinstance(result, SimulationResult)
        assert isinstance(result.time_series, pd.DataFrame)
        assert len(result.time_series) > 0

    def test_simulation_result_structure(self, sample_location, sample_system):
        """Test that simulation result has expected structure."""
        result = simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2025,
            interval_minutes=60,
        )

        # Check time series columns
        assert "power_w" in result.time_series.columns
        assert "poa_irradiance" in result.time_series.columns
        assert "cell_temperature" in result.time_series.columns
        assert "ghi" in result.time_series.columns
        assert "solar_elevation" in result.time_series.columns

    def test_simulation_statistics(self, sample_location, sample_system):
        """Test that statistics are calculated correctly."""
        result = simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2025,
            interval_minutes=60,
        )

        stats = result.statistics
        assert stats.total_energy_kwh > 0
        assert 0 < stats.capacity_factor < 1
        assert stats.peak_power_w > 0
        assert stats.average_power_w > 0
        assert stats.total_daylight_hours > 0
        assert 0 < stats.performance_ratio < 1.5

    def test_monthly_energy_calculation(self, sample_location, sample_system):
        """Test monthly energy aggregation."""
        result = simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2025,
            interval_minutes=60,
        )

        monthly_energy = result.statistics.monthly_energy_kwh
        assert len(monthly_energy) == 12
        assert all(monthly_energy >= 0)

        # Summer months should have more energy than winter
        # June (index 5) vs December (index 11)
        assert monthly_energy.iloc[5] > monthly_energy.iloc[11]

    def test_daily_energy_calculation(self, sample_location, sample_system):
        """Test daily energy aggregation."""
        result = simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2025,
            interval_minutes=60,
        )

        daily_energy = result.statistics.daily_energy_kwh
        assert len(daily_energy) >= 365  # Might be 366 for leap year
        assert all(daily_energy >= 0)

    def test_5_minute_interval(self, sample_location, sample_system):
        """Test simulation with 5-minute interval (subset for speed)."""
        # Test just 1 day to verify it works
        result = simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2025,
            interval_minutes=5,
        )

        # 5-minute intervals for a year: ~105,120 data points
        assert len(result.time_series) > 100000

    def test_with_cloud_cover(self, sample_location, sample_system):
        """Test simulation with cloud cover."""
        result_clear = simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2025,
            interval_minutes=60,
            cloud_cover=0,
        )

        result_cloudy = simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2025,
            interval_minutes=60,
            cloud_cover=50,
        )

        # Cloudy should produce less energy
        assert result_cloudy.statistics.total_energy_kwh < result_clear.statistics.total_energy_kwh

    def test_with_soiling(self, sample_location, sample_system):
        """Test simulation with soiling factor."""
        result_clean = simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2025,
            interval_minutes=60,
            soiling_factor=1.0,
        )

        result_soiled = simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2025,
            interval_minutes=60,
            soiling_factor=0.95,
        )

        # Soiled should produce less energy
        assert result_soiled.statistics.total_energy_kwh < result_clean.statistics.total_energy_kwh
        # Should be approximately 5% less
        ratio = result_soiled.statistics.total_energy_kwh / result_clean.statistics.total_energy_kwh
        assert 0.94 < ratio < 0.96

    def test_with_inverter_efficiency(self, sample_location, sample_system):
        """Test simulation with inverter efficiency."""
        result = simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2025,
            interval_minutes=60,
            inverter_efficiency=0.96,
        )

        # Should have AC power column
        assert "power_ac_w" in result.time_series.columns

        # AC power should be less than DC power
        dc_power = result.time_series["power_w"].sum()
        ac_power = result.time_series["power_ac_w"].sum()
        assert ac_power < dc_power

    def test_progress_callback(self, sample_location, sample_system):
        """Test progress callback is called."""
        progress_values = []

        def callback(progress):
            progress_values.append(progress)

        simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2025,
            interval_minutes=60,
            progress_callback=callback,
        )

        # Should have received progress updates
        assert len(progress_values) > 0
        assert progress_values[-1] == 1.0  # Final callback should be 1.0

    def test_invalid_weather_source(self, sample_location, sample_system):
        """Test that invalid weather source raises error."""
        with pytest.raises(NotImplementedError, match="not yet implemented"):
            simulate_annual(
                location=sample_location,
                system=sample_system,
                year=2025,
                interval_minutes=60,
                weather_source="openweathermap",
            )

    def test_invalid_interval(self, sample_location, sample_system):
        """Test that invalid interval raises error."""
        with pytest.raises(ValueError, match="interval_minutes must be"):
            simulate_annual(
                location=sample_location,
                system=sample_system,
                year=2025,
                interval_minutes=0,
            )

        with pytest.raises(ValueError, match="interval_minutes must be"):
            simulate_annual(
                location=sample_location,
                system=sample_system,
                year=2025,
                interval_minutes=61,
            )

    def test_different_year(self, sample_location, sample_system):
        """Test simulation for different year."""
        result = simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2024,  # Leap year
            interval_minutes=60,
        )

        # Should have data for entire year
        assert len(result.time_series) > 8760  # More than regular year

    def test_timezone_handling(self, sample_location, sample_system):
        """Test that timezone is properly handled."""
        result = simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2025,
            interval_minutes=60,
        )

        # Time series should be timezone-aware
        assert result.time_series.index.tz is not None
        assert result.time_series.index.tz.zone == "America/Denver"

    def test_nighttime_zero_power(self, sample_location, sample_system):
        """Test that nighttime produces zero power."""
        result = simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2025,
            interval_minutes=60,
        )

        # Filter to nighttime (solar elevation <= 0)
        nighttime = result.time_series[result.time_series["solar_elevation"] <= 0]

        # All nighttime power should be zero
        assert all(nighttime["power_w"] == 0)

    def test_peak_power_reasonable(self, sample_location, sample_system):
        """Test that peak power is reasonable."""
        result = simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2025,
            interval_minutes=60,
        )

        # Peak power should be less than rated power
        # Rated power at STC: 20 m² * 0.20 * 1000 W/m² = 4000 W
        # Due to temperature losses, actual peak should be a bit less
        assert result.statistics.peak_power_w < 4000
        assert result.statistics.peak_power_w > 3000  # But still significant

    def test_capacity_factor_reasonable(self, sample_location, sample_system):
        """Test that capacity factor is in reasonable range."""
        result = simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2025,
            interval_minutes=60,
        )

        # Capacity factor for solar in Colorado should be 15-25%
        assert 0.10 < result.statistics.capacity_factor < 0.30

    def test_export_functionality(self, sample_location, sample_system, tmp_path):
        """Test exporting simulation results."""
        result = simulate_annual(
            location=sample_location,
            system=sample_system,
            year=2025,
            interval_minutes=60,
        )

        filepath = tmp_path / "annual_results.csv"
        result.export_csv(str(filepath))

        assert filepath.exists()

        # Verify exported data
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        assert len(df) == len(result.time_series)
