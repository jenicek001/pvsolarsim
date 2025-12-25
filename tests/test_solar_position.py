"""Tests for solar position calculations."""

from datetime import datetime

import pytest
import pytz

from pvsolarsim.solar import calculate_solar_position


class TestSolarPosition:
    """Test suite for solar position calculations."""

    def test_solar_position_basic(self):
        """Test basic solar position calculation."""
        # Summer solstice at solar noon in Colorado
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.timezone("America/Denver"))
        pos = calculate_solar_position(timestamp, 40.0, -105.0, 1655)

        # At solar noon on summer solstice at 40°N, sun should be roughly south
        # and at high elevation (around 73.5°)
        assert 150 < pos.azimuth < 210, f"Expected south-ish azimuth, got {pos.azimuth}"
        assert 70 < pos.elevation < 80, f"Expected high elevation, got {pos.elevation}"
        assert pos.zenith == pytest.approx(90 - pos.elevation, abs=0.1)

    def test_solar_position_dataclass(self):
        """Test SolarPosition dataclass attributes."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)
        pos = calculate_solar_position(timestamp, 0, 0, 0)

        assert hasattr(pos, "azimuth")
        assert hasattr(pos, "zenith")
        assert hasattr(pos, "elevation")
        assert isinstance(pos.azimuth, float)
        assert isinstance(pos.zenith, float)
        assert isinstance(pos.elevation, float)

    def test_solar_position_night(self):
        """Test solar position at night (sun below horizon)."""
        # Midnight in Prague
        timestamp = datetime(2025, 1, 15, 0, 0, tzinfo=pytz.timezone("Europe/Prague"))
        pos = calculate_solar_position(timestamp, 49.8, 15.5, 300)

        # Sun should be well below horizon
        assert pos.elevation < 0, f"Expected negative elevation at night, got {pos.elevation}"
        assert pos.zenith > 90, f"Expected zenith > 90 at night, got {pos.zenith}"

    @pytest.mark.parametrize(
        "latitude,longitude,timestamp_utc,expected_elevation_range",
        [
            # Equator at noon on equinox - sun nearly overhead
            (0, 0, datetime(2025, 3, 20, 12, 0, tzinfo=pytz.UTC), (88, 91)),
            # Arctic circle on summer solstice - midnight sun
            (66.5, 0, datetime(2025, 6, 21, 0, 0, tzinfo=pytz.UTC), (0, 10)),
            # Southern hemisphere winter
            (-33.9, 18.4, datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC), (30, 35)),
        ],
    )
    def test_solar_elevation_by_location(
        self, latitude, longitude, timestamp_utc, expected_elevation_range
    ):
        """Test solar elevation varies correctly with latitude and season."""
        pos = calculate_solar_position(timestamp_utc, latitude, longitude, 0)
        min_elev, max_elev = expected_elevation_range

        assert (
            min_elev <= pos.elevation <= max_elev
        ), f"Expected elevation in {expected_elevation_range}, got {pos.elevation}"

    def test_invalid_latitude(self):
        """Test error handling for invalid latitude."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

        with pytest.raises(ValueError, match="Latitude must be between"):
            calculate_solar_position(timestamp, 95.0, 0, 0)

        with pytest.raises(ValueError, match="Latitude must be between"):
            calculate_solar_position(timestamp, -95.0, 0, 0)

    def test_invalid_longitude(self):
        """Test error handling for invalid longitude."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

        with pytest.raises(ValueError, match="Longitude must be between"):
            calculate_solar_position(timestamp, 0, 185.0, 0)

        with pytest.raises(ValueError, match="Longitude must be between"):
            calculate_solar_position(timestamp, 0, -185.0, 0)

    def test_naive_datetime_raises_error(self):
        """Test that naive datetime (no timezone) raises error."""
        timestamp = datetime(2025, 6, 21, 12, 0)  # No tzinfo

        with pytest.raises(ValueError, match="timezone-aware"):
            calculate_solar_position(timestamp, 49.8, 15.5, 300)

    def test_zenith_elevation_relationship(self):
        """Test that zenith + elevation ≈ 90° when sun is above horizon."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)
        pos = calculate_solar_position(timestamp, 40.0, -105.0, 1655)

        # Zenith and elevation should sum to approximately 90°
        assert pos.zenith + pos.elevation == pytest.approx(90.0, abs=0.5)

    def test_altitude_effect(self):
        """Test that altitude affects calculations (though effect is small)."""
        timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

        pos_sea_level = calculate_solar_position(timestamp, 40.0, -105.0, 0)
        pos_high_alt = calculate_solar_position(timestamp, 40.0, -105.0, 3000)

        # Positions should be similar but not identical
        assert abs(pos_sea_level.azimuth - pos_high_alt.azimuth) < 0.5
        assert abs(pos_sea_level.elevation - pos_high_alt.elevation) < 0.5

    def test_different_timezones_same_instant(self):
        """Test that different timezone representations of same instant give same result."""
        # Same instant in different timezones
        utc_time = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)
        prague_time = utc_time.astimezone(pytz.timezone("Europe/Prague"))

        pos_utc = calculate_solar_position(utc_time, 49.8, 15.5, 300)
        pos_prague = calculate_solar_position(prague_time, 49.8, 15.5, 300)

        # Should be identical
        assert pos_utc.azimuth == pytest.approx(pos_prague.azimuth, abs=0.001)
        assert pos_utc.elevation == pytest.approx(pos_prague.elevation, abs=0.001)
        assert pos_utc.zenith == pytest.approx(pos_prague.zenith, abs=0.001)
