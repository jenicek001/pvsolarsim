"""Tests for weather data file readers."""

import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
import pytz

from pvsolarsim.weather import CSVWeatherReader, JSONWeatherReader


def create_test_csv(filepath: Path, include_header: bool = True) -> None:
    """Create a test CSV file with weather data."""
    content = []
    if include_header:
        content.append("timestamp,ghi,dni,dhi,temp_air,wind_speed,cloud_cover")

    # Add some data rows
    for i in range(24):
        hour = f"{i:02d}"
        content.append(f"2025-01-01 {hour}:00:00,{100 + i},{200 + i},{50 + i},{20 + i},{2 + i * 0.1:.1f},{i * 2}")

    filepath.write_text("\n".join(content))


def test_csv_reader_standard_format():
    """Test CSV reader with standard column names."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "weather.csv"
        create_test_csv(csv_path)

        reader = CSVWeatherReader(csv_path, timezone="UTC")
        data = reader.read()

        assert isinstance(data, pd.DataFrame)
        assert len(data) == 24
        assert isinstance(data.index, pd.DatetimeIndex)
        assert data.index.tz is not None
        assert "ghi" in data.columns
        assert "temp_air" in data.columns
        assert data["ghi"].iloc[0] == 100
        assert data["temp_air"].iloc[0] == 20


def test_csv_reader_custom_column_mapping():
    """Test CSV reader with custom column names."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "custom_weather.csv"

        # Create CSV with custom column names
        content = [
            "datetime,irradiance,temperature,wind",
            "2025-01-01 00:00:00,100,20,2.0",
            "2025-01-01 01:00:00,150,21,2.5",
        ]
        csv_path.write_text("\n".join(content))

        reader = CSVWeatherReader(
            csv_path,
            column_mapping={
                "timestamp": "datetime",
                "ghi": "irradiance",
                "temp_air": "temperature",
                "wind_speed": "wind",
            },
            timezone="UTC",
        )
        data = reader.read()

        assert len(data) == 2
        assert "ghi" in data.columns
        assert "temp_air" in data.columns
        assert "wind_speed" in data.columns
        assert data["ghi"].iloc[0] == 100
        assert data["temp_air"].iloc[0] == 20


def test_csv_reader_file_not_found():
    """Test CSV reader with non-existent file."""
    with pytest.raises(FileNotFoundError):
        CSVWeatherReader("nonexistent.csv")


def test_csv_reader_missing_timestamp_column():
    """Test CSV reader with missing timestamp column."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "bad_weather.csv"

        content = [
            "ghi,temp_air",
            "100,20",
        ]
        csv_path.write_text("\n".join(content))

        reader = CSVWeatherReader(csv_path, timezone="UTC")
        with pytest.raises(ValueError, match="Timestamp column"):
            reader.read()


def test_csv_reader_date_filtering():
    """Test CSV reader with date range filtering."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "weather.csv"
        create_test_csv(csv_path)

        reader = CSVWeatherReader(csv_path, timezone="UTC")

        # Filter to specific range
        start = datetime(2025, 1, 1, 10, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2025, 1, 1, 15, 0, 0, tzinfo=pytz.UTC)
        data = reader.read(start=start, end=end)

        assert len(data) == 6  # Hours 10-15 inclusive
        assert data.index[0].hour == 10
        assert data.index[-1].hour == 15


def test_csv_reader_with_skip_rows():
    """Test CSV reader with skip_rows parameter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "weather.csv"

        # Add some header rows to skip
        content = [
            "# Weather data file",
            "# Generated on 2025-01-01",
            "timestamp,ghi,temp_air",
            "2025-01-01 00:00:00,100,20",
            "2025-01-01 01:00:00,150,21",
        ]
        csv_path.write_text("\n".join(content))

        reader = CSVWeatherReader(csv_path, skip_rows=2, timezone="UTC")
        data = reader.read()

        assert len(data) == 2
        assert data["ghi"].iloc[0] == 100


def test_csv_reader_custom_delimiter():
    """Test CSV reader with custom delimiter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "weather.tsv"

        # Create TSV file
        content = [
            "timestamp\tghi\ttemp_air",
            "2025-01-01 00:00:00\t100\t20",
            "2025-01-01 01:00:00\t150\t21",
        ]
        csv_path.write_text("\n".join(content))

        reader = CSVWeatherReader(csv_path, delimiter="\t", timezone="UTC")
        data = reader.read()

        assert len(data) == 2
        assert data["ghi"].iloc[0] == 100


def test_json_reader_basic():
    """Test JSON reader with basic data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "weather.json"

        # Create JSON file
        json_data = [
            {
                "timestamp": "2025-01-01T00:00:00Z",
                "ghi": 100,
                "temp_air": 20,
                "wind_speed": 2.0,
            },
            {
                "timestamp": "2025-01-01T01:00:00Z",
                "ghi": 150,
                "temp_air": 21,
                "wind_speed": 2.5,
            },
        ]
        import json

        json_path.write_text(json.dumps(json_data))

        reader = JSONWeatherReader(json_path, timezone="UTC")
        data = reader.read()

        assert len(data) == 2
        assert "ghi" in data.columns
        assert "temp_air" in data.columns
        assert data["ghi"].iloc[0] == 100


def test_json_reader_missing_timestamp():
    """Test JSON reader with missing timestamp field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "bad_weather.json"

        json_data = [
            {
                "ghi": 100,
                "temp_air": 20,
            }
        ]
        import json

        json_path.write_text(json.dumps(json_data))

        reader = JSONWeatherReader(json_path, timezone="UTC")
        with pytest.raises(ValueError, match="timestamp"):
            reader.read()


def test_json_reader_file_not_found():
    """Test JSON reader with non-existent file."""
    with pytest.raises(FileNotFoundError):
        JSONWeatherReader("nonexistent.json")


def test_csv_reader_timezone_conversion():
    """Test CSV reader handles timezone conversion correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "weather.csv"

        # Create CSV with timezone-aware timestamps
        content = [
            "timestamp,ghi,temp_air",
            "2025-01-01T00:00:00+00:00,100,20",
            "2025-01-01T01:00:00+00:00,150,21",
        ]
        csv_path.write_text("\n".join(content))

        reader = CSVWeatherReader(csv_path, timezone="America/Denver")
        data = reader.read()

        # Should be converted to Denver time
        assert data.index.tz.zone == "America/Denver"
