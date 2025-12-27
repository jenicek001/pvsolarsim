"""Tests for weather data interpolation module."""

import numpy as np
import pandas as pd
import pytest

from pvsolarsim.weather.interpolation import (
    backward_fill,
    detect_gaps,
    fill_gaps,
    forward_fill,
    interpolate_weather_data,
)


class TestInterpolateWeatherData:
    """Tests for interpolate_weather_data function."""

    def test_linear_interpolation(self):
        """Test linear interpolation fills gaps correctly."""
        data = pd.DataFrame(
            {"ghi": [100.0, np.nan, np.nan, 400.0], "temp_air": [20.0, np.nan, 25.0, np.nan]},
            index=pd.date_range("2025-01-01", periods=4, freq="h", tz="UTC"),
        )

        result = interpolate_weather_data(data, method="linear")

        assert result["ghi"].tolist() == [100.0, 200.0, 300.0, 400.0]
        assert result["temp_air"].iloc[1] == pytest.approx(22.5)

    def test_limit_parameter(self):
        """Test limit parameter restricts number of consecutive fills."""
        data = pd.DataFrame(
            {"ghi": [100.0, np.nan, np.nan, np.nan, 500.0]},
            index=pd.date_range("2025-01-01", periods=5, freq="h", tz="UTC"),
        )

        # Only fill up to 2 consecutive NaNs from forward direction
        result = interpolate_weather_data(data, method="linear", limit=2, limit_direction="forward")

        # First two NaNs should be filled, third should remain NaN
        assert not np.isnan(result["ghi"].iloc[1])
        assert not np.isnan(result["ghi"].iloc[2])
        assert np.isnan(result["ghi"].iloc[3])

    def test_no_missing_values(self):
        """Test that data without missing values is unchanged."""
        data = pd.DataFrame(
            {"ghi": [100.0, 200.0, 300.0], "temp_air": [20.0, 25.0, 30.0]},
            index=pd.date_range("2025-01-01", periods=3, freq="h", tz="UTC"),
        )

        result = interpolate_weather_data(data, method="linear")

        pd.testing.assert_frame_equal(result, data)


class TestForwardFill:
    """Tests for forward_fill function."""

    def test_forward_fill_basic(self):
        """Test basic forward fill functionality."""
        data = pd.DataFrame(
            {"ghi": [100.0, np.nan, np.nan, 400.0]},
            index=pd.date_range("2025-01-01", periods=4, freq="h", tz="UTC"),
        )

        result = forward_fill(data)

        assert result["ghi"].tolist() == [100.0, 100.0, 100.0, 400.0]

    def test_forward_fill_with_limit(self):
        """Test forward fill with limit parameter."""
        data = pd.DataFrame(
            {"ghi": [100.0, np.nan, np.nan, np.nan]},
            index=pd.date_range("2025-01-01", periods=4, freq="h", tz="UTC"),
        )

        result = forward_fill(data, limit=2)

        # Only first 2 NaNs should be filled
        assert result["ghi"].iloc[0] == 100.0
        assert result["ghi"].iloc[1] == 100.0
        assert result["ghi"].iloc[2] == 100.0
        assert np.isnan(result["ghi"].iloc[3])

    def test_forward_fill_specific_columns(self):
        """Test forward fill on specific columns only."""
        data = pd.DataFrame(
            {"ghi": [100.0, np.nan, 300.0], "temp_air": [20.0, np.nan, 30.0]},
            index=pd.date_range("2025-01-01", periods=3, freq="h", tz="UTC"),
        )

        result = forward_fill(data, columns=["ghi"])

        # ghi should be filled, temp_air should not
        assert result["ghi"].iloc[1] == 100.0
        assert np.isnan(result["temp_air"].iloc[1])


class TestBackwardFill:
    """Tests for backward_fill function."""

    def test_backward_fill_basic(self):
        """Test basic backward fill functionality."""
        data = pd.DataFrame(
            {"ghi": [np.nan, np.nan, 300.0, 400.0]},
            index=pd.date_range("2025-01-01", periods=4, freq="h", tz="UTC"),
        )

        result = backward_fill(data)

        assert result["ghi"].tolist() == [300.0, 300.0, 300.0, 400.0]

    def test_backward_fill_with_limit(self):
        """Test backward fill with limit parameter."""
        data = pd.DataFrame(
            {"ghi": [np.nan, np.nan, np.nan, 400.0]},
            index=pd.date_range("2025-01-01", periods=4, freq="h", tz="UTC"),
        )

        result = backward_fill(data, limit=2)

        # Only last 2 NaNs should be filled
        assert np.isnan(result["ghi"].iloc[0])
        assert result["ghi"].iloc[1] == 400.0
        assert result["ghi"].iloc[2] == 400.0
        assert result["ghi"].iloc[3] == 400.0


class TestDetectGaps:
    """Tests for detect_gaps function."""

    def test_no_gaps(self):
        """Test detection when there are no gaps."""
        data = pd.DataFrame(
            {"ghi": [100.0, 200.0, 300.0]},
            index=pd.date_range("2025-01-01", periods=3, freq="h", tz="UTC"),
        )

        gaps = detect_gaps(data, expected_freq="h")

        assert len(gaps) == 0

    def test_single_gap(self):
        """Test detection of a single gap."""
        data = pd.DataFrame(
            {"ghi": [100.0, 200.0, 300.0]},
            index=pd.to_datetime(
                ["2025-01-01 00:00", "2025-01-01 01:00", "2025-01-01 05:00"], utc=True
            ),
        )

        gaps = detect_gaps(data, expected_freq="h")

        assert len(gaps) == 1
        assert gaps.iloc[0]["missing_points"] == 3
        assert gaps.iloc[0]["gap_start"] == pd.Timestamp("2025-01-01 02:00", tz="UTC")
        assert gaps.iloc[0]["gap_end"] == pd.Timestamp("2025-01-01 04:00", tz="UTC")

    def test_multiple_gaps(self):
        """Test detection of multiple gaps."""
        data = pd.DataFrame(
            {"ghi": [100.0, 200.0, 300.0, 400.0]},
            index=pd.to_datetime(
                [
                    "2025-01-01 00:00",
                    "2025-01-01 03:00",
                    "2025-01-01 04:00",
                    "2025-01-01 07:00",
                ],
                utc=True,
            ),
        )

        gaps = detect_gaps(data, expected_freq="h")

        assert len(gaps) == 2
        assert gaps.iloc[0]["missing_points"] == 2  # Gap 1: 01:00 and 02:00
        assert gaps.iloc[1]["missing_points"] == 2  # Gap 2: 05:00 and 06:00

    def test_requires_datetime_index(self):
        """Test that non-datetime index raises error."""
        data = pd.DataFrame({"ghi": [100.0, 200.0, 300.0]})

        with pytest.raises(ValueError, match="must have a DatetimeIndex"):
            detect_gaps(data)


class TestFillGaps:
    """Tests for fill_gaps function."""

    def test_fill_gaps_linear(self):
        """Test gap filling with linear interpolation."""
        data = pd.DataFrame(
            {"ghi": [100.0, 400.0]},
            index=pd.to_datetime(["2025-01-01 00:00", "2025-01-01 04:00"], utc=True),
        )

        result = fill_gaps(data, method="linear", expected_freq="h")

        assert len(result) == 5  # 0, 1, 2, 3, 4
        assert result["ghi"].iloc[0] == 100.0
        assert result["ghi"].iloc[2] == 250.0  # Interpolated
        assert result["ghi"].iloc[4] == 400.0

    def test_fill_gaps_forward(self):
        """Test gap filling with forward fill."""
        data = pd.DataFrame(
            {"ghi": [100.0, 400.0]},
            index=pd.to_datetime(["2025-01-01 00:00", "2025-01-01 03:00"], utc=True),
        )

        result = fill_gaps(data, method="forward", expected_freq="h")

        assert len(result) == 4
        assert result["ghi"].iloc[1] == 100.0  # Forward filled
        assert result["ghi"].iloc[2] == 100.0  # Forward filled
        assert result["ghi"].iloc[3] == 400.0

    def test_fill_gaps_max_size(self):
        """Test that large gaps are not filled when max_gap_size is set."""
        data = pd.DataFrame(
            {"ghi": [100.0, 400.0]},
            index=pd.to_datetime(["2025-01-01 00:00", "2025-01-01 10:00"], utc=True),
        )

        result = fill_gaps(data, method="linear", max_gap_size=3, expected_freq="h")

        # Gap is 9 points, larger than max_gap_size=3, should have NaNs
        assert np.isnan(result["ghi"].iloc[5])  # Middle point should be NaN

    def test_fill_gaps_both_directions(self):
        """Test gap filling with both forward and backward fill."""
        data = pd.DataFrame(
            {"ghi": [100.0, np.nan, 300.0]},
            index=pd.date_range("2025-01-01", periods=3, freq="h", tz="UTC"),
        )

        result = fill_gaps(data, method="both", expected_freq="h")

        # Should fill from both directions
        assert result["ghi"].iloc[1] == 100.0  # Forward filled

    def test_invalid_method(self):
        """Test that invalid method raises error."""
        data = pd.DataFrame(
            {"ghi": [100.0, 400.0]},
            index=pd.to_datetime(["2025-01-01 00:00", "2025-01-01 02:00"], utc=True),
        )

        with pytest.raises(ValueError, match="Unknown method"):
            fill_gaps(data, method="invalid_method", expected_freq="h")
