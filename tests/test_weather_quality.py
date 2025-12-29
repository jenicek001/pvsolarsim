"""Tests for weather data quality checks module."""

import pandas as pd

from pvsolarsim.weather.quality import (
    QualityFlags,
    check_irradiance_consistency,
    check_negative_values,
    check_nighttime_irradiance,
    check_value_ranges,
    create_quality_report,
    perform_quality_checks,
)


class TestCheckNighttimeIrradiance:
    """Tests for check_nighttime_irradiance function."""

    def test_daytime_irradiance_ok(self):
        """Test that daytime irradiance doesn't get flagged."""
        # Create data for midday (high GHI is expected)
        data = pd.DataFrame(
            {"ghi": [800.0, 900.0, 850.0]},
            index=pd.date_range("2025-06-21 12:00", periods=3, freq="h", tz="UTC"),
        )

        flags = check_nighttime_irradiance(data, latitude=40.0, longitude=-105.0)

        # Daytime values should not be flagged
        assert not flags.any()

    def test_nighttime_irradiance_flagged(self):
        """Test that nighttime irradiance gets flagged."""
        # Create data for early morning when sun is below horizon
        # At 40°N, -105°W on Dec 21, 5 AM UTC should be nighttime
        data = pd.DataFrame(
            {"ghi": [0.0, 50.0, 0.0]},  # Middle value is suspicious
            index=pd.date_range("2025-12-21 05:00", periods=3, freq="h", tz="UTC"),
        )

        flags = check_nighttime_irradiance(data, latitude=40.0, longitude=-105.0, threshold=10.0)

        # Middle value should be flagged
        assert flags.iloc[1]
        assert not flags.iloc[0]
        assert not flags.iloc[2]

    def test_no_ghi_column(self):
        """Test that missing GHI column returns all False."""
        data = pd.DataFrame(
            {"temp_air": [20.0, 25.0, 30.0]},
            index=pd.date_range("2025-01-01", periods=3, freq="h", tz="UTC"),
        )

        flags = check_nighttime_irradiance(data, latitude=40.0, longitude=-105.0)

        assert not flags.any()


class TestCheckValueRanges:
    """Tests for check_value_ranges function."""

    def test_all_values_in_range(self):
        """Test that valid values don't get flagged."""
        data = pd.DataFrame(
            {
                "ghi": [100.0, 800.0, 1200.0],
                "dni": [0.0, 900.0, 1400.0],
                "dhi": [50.0, 200.0, 500.0],
                "temp_air": [-10.0, 25.0, 50.0],
                "wind_speed": [0.0, 5.0, 15.0],
                "cloud_cover": [0.0, 50.0, 100.0],
            },
            index=pd.date_range("2025-01-01", periods=3, freq="h", tz="UTC"),
        )

        flags = check_value_ranges(data)

        assert not flags.any()

    def test_ghi_out_of_range(self):
        """Test that out-of-range GHI gets flagged."""
        data = pd.DataFrame(
            {"ghi": [100.0, 2000.0, 300.0]},  # 2000 is too high
            index=pd.date_range("2025-01-01", periods=3, freq="h", tz="UTC"),
        )

        flags = check_value_ranges(data)

        assert flags.iloc[1]
        assert not flags.iloc[0]
        assert not flags.iloc[2]

    def test_temperature_out_of_range(self):
        """Test that extreme temperatures get flagged."""
        data = pd.DataFrame(
            {
                "ghi": [100.0, 200.0, 300.0],
                "temp_air": [20.0, 100.0, 25.0],  # 100 is too high
            },
            index=pd.date_range("2025-01-01", periods=3, freq="h", tz="UTC"),
        )

        flags = check_value_ranges(data)

        assert flags.iloc[1]

    def test_multiple_columns_out_of_range(self):
        """Test that multiple out-of-range values get flagged."""
        data = pd.DataFrame(
            {
                "ghi": [2000.0, 200.0],  # First too high
                "temp_air": [20.0, 100.0],  # Second too high
            },
            index=pd.date_range("2025-01-01", periods=2, freq="h", tz="UTC"),
        )

        flags = check_value_ranges(data)

        # Both rows should be flagged
        assert flags.iloc[0]
        assert flags.iloc[1]


class TestCheckNegativeValues:
    """Tests for check_negative_values function."""

    def test_no_negative_values(self):
        """Test that non-negative values don't get flagged."""
        data = pd.DataFrame(
            {"ghi": [0.0, 100.0, 200.0], "temp_air": [-10.0, 0.0, 20.0]},
            index=pd.date_range("2025-01-01", periods=3, freq="h", tz="UTC"),
        )

        flags = check_negative_values(data)

        # temp_air can be negative, so no flags
        assert not flags.any()

    def test_negative_ghi_flagged(self):
        """Test that negative GHI gets flagged."""
        data = pd.DataFrame(
            {"ghi": [100.0, -50.0, 200.0]},
            index=pd.date_range("2025-01-01", periods=3, freq="h", tz="UTC"),
        )

        flags = check_negative_values(data)

        assert flags.iloc[1]
        assert not flags.iloc[0]
        assert not flags.iloc[2]

    def test_negative_wind_speed_flagged(self):
        """Test that negative wind speed gets flagged."""
        data = pd.DataFrame(
            {"ghi": [100.0, 200.0], "wind_speed": [5.0, -2.0]},
            index=pd.date_range("2025-01-01", periods=2, freq="h", tz="UTC"),
        )

        flags = check_negative_values(data)

        assert flags.iloc[1]


class TestCheckIrradianceConsistency:
    """Tests for check_irradiance_consistency function."""

    def test_consistent_irradiance(self):
        """Test that consistent irradiance values don't get flagged."""
        # Create consistent data: GHI ≈ DHI + DNI*cos(zenith)
        data = pd.DataFrame(
            {
                "ghi": [800.0, 850.0, 900.0],
                "dni": [900.0, 950.0, 1000.0],
                "dhi": [150.0, 150.0, 150.0],
            },
            # Summer midday - high sun angle
            index=pd.date_range("2025-06-21 11:00", periods=3, freq="h", tz="UTC"),
        )

        flags = check_irradiance_consistency(data, latitude=40.0, longitude=-105.0, tolerance=200.0)

        # Allow some tolerance for atmospheric effects
        # Should mostly be consistent
        assert flags.sum() <= 2  # At most 2 flagged out of 3

    def test_inconsistent_irradiance(self):
        """Test that inconsistent irradiance gets flagged."""
        data = pd.DataFrame(
            {
                "ghi": [100.0, 200.0, 300.0],  # GHI too low
                "dni": [900.0, 900.0, 900.0],
                "dhi": [150.0, 150.0, 150.0],
            },
            # Summer midday
            index=pd.date_range("2025-06-21 12:00", periods=3, freq="h", tz="UTC"),
        )

        flags = check_irradiance_consistency(data, latitude=40.0, longitude=-105.0, tolerance=50.0)

        # All should be flagged (GHI much lower than expected)
        assert flags.all()

    def test_missing_components(self):
        """Test that missing components don't cause errors."""
        data = pd.DataFrame(
            {"ghi": [100.0, 200.0], "temp_air": [20.0, 25.0]},  # Missing DNI and DHI
            index=pd.date_range("2025-01-01", periods=2, freq="h", tz="UTC"),
        )

        flags = check_irradiance_consistency(data, latitude=40.0, longitude=-105.0)

        # Should return all False when components are missing
        assert not flags.any()


class TestPerformQualityChecks:
    """Tests for perform_quality_checks function."""

    def test_quality_checks_integration(self):
        """Test that all quality checks work together."""
        data = pd.DataFrame(
            {
                "ghi": [100.0, -50.0, 2000.0, 100.0],  # negative, out of range
                "dni": [200.0, 300.0, 400.0, 500.0],
                "dhi": [50.0, 75.0, 100.0, 75.0],
                "temp_air": [20.0, 25.0, 100.0, 20.0],  # out of range
            },
            index=pd.date_range("2025-06-21 12:00", periods=4, freq="h", tz="UTC"),
        )

        flags = perform_quality_checks(data, latitude=40.0, longitude=-105.0)

        # Check that quality flags object is created correctly
        assert isinstance(flags, QualityFlags)
        assert hasattr(flags, "nighttime_ghi")
        assert hasattr(flags, "negative_values")
        assert hasattr(flags, "out_of_range")
        assert hasattr(flags, "inconsistent")

        # Check summary
        summary = flags.summary()
        assert "total_issues" in summary
        assert "quality_percentage" in summary
        assert summary["total_points"] == 4

        # Should have multiple issues flagged
        assert summary["total_issues"] > 0


class TestQualityFlags:
    """Tests for QualityFlags dataclass."""

    def test_any_issues_property(self):
        """Test that any_issues property combines all flags correctly."""
        index = pd.date_range("2025-01-01", periods=4, freq="h", tz="UTC")

        flags = QualityFlags(
            nighttime_ghi=pd.Series([True, False, False, False], index=index),
            negative_values=pd.Series([False, True, False, False], index=index),
            out_of_range=pd.Series([False, False, True, False], index=index),
            inconsistent=pd.Series([False, False, False, True], index=index),
        )

        any_issues = flags.any_issues

        # All rows should be flagged (each has one issue)
        assert any_issues.all()

    def test_summary_calculation(self):
        """Test that summary calculates metrics correctly."""
        index = pd.date_range("2025-01-01", periods=4, freq="h", tz="UTC")

        flags = QualityFlags(
            nighttime_ghi=pd.Series([True, False, False, False], index=index),
            negative_values=pd.Series([True, True, False, False], index=index),
            out_of_range=pd.Series([False, False, False, False], index=index),
            inconsistent=pd.Series([False, False, False, False], index=index),
        )

        summary = flags.summary()

        assert summary["nighttime_ghi_count"] == 1
        assert summary["negative_values_count"] == 2
        assert summary["total_issues"] == 2  # Two rows have issues
        assert summary["total_points"] == 4
        assert summary["quality_percentage"] == 50.0  # 2 good out of 4


class TestCreateQualityReport:
    """Tests for create_quality_report function."""

    def test_report_generation(self):
        """Test that quality report is generated correctly."""
        data = pd.DataFrame(
            {"ghi": [100.0, -50.0, 200.0], "temp_air": [20.0, 25.0, 30.0]},
            index=pd.date_range("2025-01-01", periods=3, freq="h", tz="UTC"),
        )

        flags = perform_quality_checks(data, latitude=40.0, longitude=-105.0)
        report = create_quality_report(data, flags)

        # Check that report contains expected sections
        assert "WEATHER DATA QUALITY REPORT" in report
        assert "Total data points:" in report
        assert "Quality percentage:" in report
        assert "Issue Summary:" in report

    def test_report_with_no_issues(self):
        """Test report generation when there are no issues."""
        data = pd.DataFrame(
            {"ghi": [100.0, 200.0, 300.0], "temp_air": [20.0, 25.0, 30.0]},
            index=pd.date_range("2025-06-21 12:00", periods=3, freq="h", tz="UTC"),
        )

        flags = perform_quality_checks(data, latitude=40.0, longitude=-105.0)
        report = create_quality_report(data, flags)

        assert "100.00%" in report or "Quality percentage" in report

    def test_report_save_to_file(self, tmp_path):
        """Test that report can be saved to file."""
        data = pd.DataFrame(
            {"ghi": [100.0, 200.0], "temp_air": [20.0, 25.0]},
            index=pd.date_range("2025-01-01", periods=2, freq="h", tz="UTC"),
        )

        flags = perform_quality_checks(data, latitude=40.0, longitude=-105.0)
        output_file = tmp_path / "quality_report.txt"

        create_quality_report(data, flags, output_file=str(output_file))

        # Check file was created and contains content
        assert output_file.exists()
        content = output_file.read_text()
        assert "WEATHER DATA QUALITY REPORT" in content
