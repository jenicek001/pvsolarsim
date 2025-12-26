"""Tests for time series generation utilities."""

from datetime import datetime

import pandas as pd
import pytest
import pytz

from pvsolarsim.simulation.timeseries import generate_time_series


class TestGenerateTimeSeries:
    """Test suite for time series generation."""

    def test_basic_time_series(self):
        """Test basic time series generation."""
        start = datetime(2025, 1, 1, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2025, 1, 2, 0, 0, tzinfo=pytz.UTC)

        times = generate_time_series(start, end, interval_minutes=60)

        assert isinstance(times, pd.DatetimeIndex)
        assert len(times) == 25  # 24 hours + 1 (0:00 to 24:00)
        assert times[0] == start
        assert times[-1] == end

    def test_5_minute_interval(self):
        """Test 5-minute interval time series."""
        start = datetime(2025, 1, 1, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2025, 1, 1, 1, 0, tzinfo=pytz.UTC)

        times = generate_time_series(start, end, interval_minutes=5)

        assert len(times) == 13  # 0, 5, 10, ..., 60 minutes
        assert (times[1] - times[0]).total_seconds() == 300  # 5 minutes

    def test_15_minute_interval(self):
        """Test 15-minute interval time series."""
        start = datetime(2025, 1, 1, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2025, 1, 1, 1, 0, tzinfo=pytz.UTC)

        times = generate_time_series(start, end, interval_minutes=15)

        assert len(times) == 5  # 0, 15, 30, 45, 60 minutes

    def test_naive_datetime_with_timezone(self):
        """Test naive datetime with timezone parameter."""
        start = datetime(2025, 1, 1, 0, 0)
        end = datetime(2025, 1, 2, 0, 0)

        times = generate_time_series(start, end, interval_minutes=60, timezone="UTC")

        assert times.tz is not None
        assert len(times) == 25

    def test_naive_datetime_without_timezone_raises(self):
        """Test that naive datetime without timezone raises error."""
        start = datetime(2025, 1, 1, 0, 0)
        end = datetime(2025, 1, 2, 0, 0)

        with pytest.raises(ValueError, match="Timezone parameter required"):
            generate_time_series(start, end, interval_minutes=60)

    def test_different_timezone(self):
        """Test time series with different timezone."""
        tz = pytz.timezone("America/Denver")
        start = tz.localize(datetime(2025, 1, 1, 0, 0))
        end = tz.localize(datetime(2025, 1, 2, 0, 0))

        times = generate_time_series(start, end, interval_minutes=60)

        assert times.tz.zone == "America/Denver"
        assert len(times) == 25

    def test_annual_time_series(self):
        """Test generating annual time series."""
        start = datetime(2025, 1, 1, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2025, 12, 31, 23, 59, tzinfo=pytz.UTC)

        times = generate_time_series(start, end, interval_minutes=60)

        # Should have ~8760 hours in a year
        assert len(times) >= 8760
        assert times[0].year == 2025
        assert times[-1].year == 2025

    def test_invalid_interval_too_small(self):
        """Test that interval < 1 raises error."""
        start = datetime(2025, 1, 1, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2025, 1, 2, 0, 0, tzinfo=pytz.UTC)

        with pytest.raises(ValueError, match="interval_minutes must be"):
            generate_time_series(start, end, interval_minutes=0)

    def test_invalid_interval_too_large(self):
        """Test that interval > 1440 raises error."""
        start = datetime(2025, 1, 1, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2025, 1, 2, 0, 0, tzinfo=pytz.UTC)

        with pytest.raises(ValueError, match="interval_minutes must be"):
            generate_time_series(start, end, interval_minutes=1441)

    def test_timezone_aware_result(self):
        """Test that result is always timezone-aware."""
        start = datetime(2025, 1, 1, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2025, 1, 2, 0, 0, tzinfo=pytz.UTC)

        times = generate_time_series(start, end, interval_minutes=60)

        assert times.tz is not None
        # All times should be timezone-aware
        for t in times[:5]:  # Check first 5
            assert t.tzinfo is not None

    def test_1_minute_interval(self):
        """Test 1-minute interval."""
        start = datetime(2025, 1, 1, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2025, 1, 1, 0, 10, tzinfo=pytz.UTC)

        times = generate_time_series(start, end, interval_minutes=1)

        assert len(times) == 11  # 0 to 10 minutes inclusive
        assert (times[1] - times[0]).total_seconds() == 60

    def test_daylight_only_parameter(self):
        """Test daylight_only parameter (currently no-op)."""
        start = datetime(2025, 1, 1, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2025, 1, 2, 0, 0, tzinfo=pytz.UTC)

        # Should not raise error, but doesn't filter yet
        times = generate_time_series(start, end, interval_minutes=60, daylight_only=True)

        assert len(times) == 25  # Currently returns all times
