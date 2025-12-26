"""Tests for power calculation."""

from datetime import datetime

import pytest
import pytz

from pvsolarsim import Location, PowerResult, PVSystem, calculate_power


class TestCalculatePower:
    """Test power calculation function."""

    @pytest.fixture
    def location(self):
        """Create test location."""
        return Location(latitude=49.8, longitude=15.5, altitude=300, timezone="Europe/Prague")

    @pytest.fixture
    def system(self):
        """Create test PV system."""
        return PVSystem(
            panel_area=20.0,
            panel_efficiency=0.20,
            tilt=35.0,
            azimuth=180.0,
            temp_coefficient=-0.004,
        )

    def test_basic_calculation(self, location, system):
        """Test basic power calculation."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)
        result = calculate_power(location, system, timestamp, ambient_temp=25, wind_speed=3)

        assert isinstance(result, PowerResult)
        assert result.power_w > 0
        assert result.poa_irradiance > 0
        assert result.solar_elevation > 0

    def test_with_cloud_cover(self, location, system):
        """Test power calculation with cloud cover."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

        # Clear sky
        result_clear = calculate_power(location, system, timestamp, cloud_cover=0)

        # 50% cloud cover
        result_cloudy = calculate_power(location, system, timestamp, cloud_cover=50)

        # Cloudy should produce less power
        assert result_cloudy.power_w < result_clear.power_w
        assert result_cloudy.poa_irradiance < result_clear.poa_irradiance

    def test_with_provided_irradiance(self, location, system):
        """Test power calculation with user-provided irradiance."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)
        result = calculate_power(
            location,
            system,
            timestamp,
            ghi=800,
            dni=700,
            dhi=150,
            ambient_temp=25,
            wind_speed=3,
        )

        assert result.power_w > 0
        assert result.ghi == 800
        assert result.dni == 700
        assert result.dhi == 150

    def test_nighttime_zero_power(self, location, system):
        """Test that nighttime produces zero power."""
        timestamp = datetime(2025, 6, 21, 0, 0, tzinfo=pytz.UTC)
        result = calculate_power(location, system, timestamp)

        assert result.power_w == 0
        assert result.poa_irradiance == 0
        assert result.solar_elevation <= 0

    def test_temperature_effect(self, location, system):
        """Test temperature effect on power."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

        # Cold temperature
        result_cold = calculate_power(location, system, timestamp, ambient_temp=10)

        # Hot temperature
        result_hot = calculate_power(location, system, timestamp, ambient_temp=40)

        # Cold should produce more power (higher temperature correction factor)
        assert result_cold.power_w > result_hot.power_w
        assert result_cold.temperature_factor > result_hot.temperature_factor

    def test_soiling_factor(self, location, system):
        """Test soiling factor reduces power."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

        # Clean panels
        result_clean = calculate_power(location, system, timestamp, soiling_factor=1.0)

        # Dirty panels (10% loss)
        result_dirty = calculate_power(location, system, timestamp, soiling_factor=0.9)

        assert result_dirty.power_w == pytest.approx(result_clean.power_w * 0.9, rel=0.01)

    def test_degradation_factor(self, location, system):
        """Test degradation factor reduces power."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

        # New panels
        result_new = calculate_power(location, system, timestamp, degradation_factor=1.0)

        # Degraded panels (5% loss)
        result_degraded = calculate_power(
            location, system, timestamp, degradation_factor=0.95
        )

        assert result_degraded.power_w == pytest.approx(result_new.power_w * 0.95, rel=0.01)

    def test_inverter_efficiency(self, location, system):
        """Test AC power calculation with inverter efficiency."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

        # Without inverter
        result_dc = calculate_power(location, system, timestamp)
        assert result_dc.power_ac_w is None

        # With inverter (95% efficiency)
        result_ac = calculate_power(location, system, timestamp, inverter_efficiency=0.95)
        assert result_ac.power_ac_w is not None
        assert result_ac.power_ac_w == pytest.approx(result_ac.power_w * 0.95, rel=0.01)

    def test_different_locations(self):
        """Test power calculation at different locations."""
        system = PVSystem(20.0, 0.20, 35.0, 180.0)
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

        # Equator
        loc_equator = Location(0, 0, 0)
        result_equator = calculate_power(loc_equator, system, timestamp)

        # High latitude
        loc_north = Location(60, 0, 0)
        result_north = calculate_power(loc_north, system, timestamp)

        # Both should produce power at noon on summer solstice
        assert result_equator.power_w > 0
        assert result_north.power_w > 0

    def test_different_seasons(self, location, system):
        """Test power calculation in different seasons."""
        # Summer solstice
        summer = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)
        result_summer = calculate_power(location, system, summer)

        # Winter solstice
        winter = datetime(2025, 12, 21, 12, 0, tzinfo=pytz.UTC)
        result_winter = calculate_power(location, system, winter)

        # Summer should produce more power (higher sun angle)
        assert result_summer.power_w > result_winter.power_w
        assert result_summer.solar_elevation > result_winter.solar_elevation

    def test_different_orientations(self, location):
        """Test power with different panel orientations."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

        # South-facing (optimal in northern hemisphere)
        system_south = PVSystem(20.0, 0.20, 35.0, 180.0)
        result_south = calculate_power(location, system_south, timestamp)

        # North-facing (suboptimal)
        system_north = PVSystem(20.0, 0.20, 35.0, 0.0)
        result_north = calculate_power(location, system_north, timestamp)

        # South should produce more power
        assert result_south.power_w > result_north.power_w

    def test_different_tilts(self, location):
        """Test power with different panel tilts."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

        # Optimal tilt (latitude-based)
        system_optimal = PVSystem(20.0, 0.20, 35.0, 180.0)
        result_optimal = calculate_power(location, system_optimal, timestamp)

        # Flat panels
        system_flat = PVSystem(20.0, 0.20, 0.0, 180.0)
        result_flat = calculate_power(location, system_flat, timestamp)

        # Both should produce power
        assert result_optimal.power_w > 0
        assert result_flat.power_w > 0

    def test_power_result_attributes(self, location, system):
        """Test that PowerResult has all expected attributes."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)
        result = calculate_power(location, system, timestamp)

        assert hasattr(result, "power_w")
        assert hasattr(result, "poa_irradiance")
        assert hasattr(result, "poa_direct")
        assert hasattr(result, "poa_diffuse")
        assert hasattr(result, "cell_temperature")
        assert hasattr(result, "ghi")
        assert hasattr(result, "dni")
        assert hasattr(result, "dhi")
        assert hasattr(result, "solar_elevation")
        assert hasattr(result, "solar_azimuth")
        assert hasattr(result, "temperature_factor")
        assert hasattr(result, "power_ac_w")

    def test_invalid_timestamp(self, location, system):
        """Test error with non-timezone-aware timestamp."""
        timestamp = datetime(2025, 6, 21, 12, 0)  # No timezone

        with pytest.raises(ValueError, match="timezone-aware"):
            calculate_power(location, system, timestamp)


class TestPowerCalculationEdgeCases:
    """Test edge cases in power calculation."""

    def test_very_high_irradiance(self):
        """Test with very high irradiance."""
        location = Location(0, 0, 0)
        system = PVSystem(20.0, 0.20, 0.0, 180.0)
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

        result = calculate_power(
            location, system, timestamp, ghi=1500, dni=1400, dhi=100
        )

        assert result.power_w > 0
        assert result.power_w < 10000  # Reasonable upper limit

    def test_extreme_cold(self):
        """Test with extreme cold temperature."""
        location = Location(49.8, 15.5, 300)
        system = PVSystem(20.0, 0.20, 35.0, 180.0)
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

        result = calculate_power(location, system, timestamp, ambient_temp=-30)

        assert result.power_w > 0
        # Cell temperature will be warmer than ambient due to solar heating
        assert result.cell_temperature > -30
        assert result.cell_temperature < 30  # But still cool

    def test_extreme_heat(self):
        """Test with extreme heat."""
        location = Location(49.8, 15.5, 300)
        system = PVSystem(20.0, 0.20, 35.0, 180.0)
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

        result = calculate_power(location, system, timestamp, ambient_temp=50)

        assert result.power_w > 0
        assert result.cell_temperature > 50

    def test_high_wind_speed(self):
        """Test with high wind speed (better cooling)."""
        location = Location(49.8, 15.5, 300)
        system = PVSystem(20.0, 0.20, 35.0, 180.0)
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

        # Low wind
        result_low_wind = calculate_power(location, system, timestamp, wind_speed=1)

        # High wind
        result_high_wind = calculate_power(location, system, timestamp, wind_speed=10)

        # High wind should cool panels better, leading to higher power
        assert result_high_wind.cell_temperature < result_low_wind.cell_temperature

    def test_full_cloud_cover(self):
        """Test with 100% cloud cover."""
        location = Location(49.8, 15.5, 300)
        system = PVSystem(20.0, 0.20, 35.0, 180.0)
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

        result_clear = calculate_power(location, system, timestamp, cloud_cover=0)
        result_cloudy = calculate_power(location, system, timestamp, cloud_cover=100)

        # Should still produce some power (diffuse light)
        assert result_cloudy.power_w > 0
        # But significantly reduced compared to clear sky
        assert result_cloudy.power_w < result_clear.power_w * 0.7

    def test_polar_region_summer(self):
        """Test polar region during summer (midnight sun)."""
        location = Location(70, 15, 0)  # Northern Norway
        system = PVSystem(20.0, 0.20, 35.0, 180.0)
        timestamp = datetime(2025, 6, 21, 23, 0, tzinfo=pytz.UTC)  # Near midnight

        result = calculate_power(location, system, timestamp)

        # Might produce some power due to midnight sun
        assert result.power_w >= 0

    def test_combined_losses(self):
        """Test with combined soiling and degradation."""
        location = Location(49.8, 15.5, 300)
        system = PVSystem(20.0, 0.20, 35.0, 180.0)
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

        result_ideal = calculate_power(
            location, system, timestamp, soiling_factor=1.0, degradation_factor=1.0
        )

        result_losses = calculate_power(
            location, system, timestamp, soiling_factor=0.95, degradation_factor=0.97
        )

        expected_factor = 0.95 * 0.97
        assert result_losses.power_w == pytest.approx(
            result_ideal.power_w * expected_factor, rel=0.01
        )
