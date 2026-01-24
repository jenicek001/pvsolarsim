"""Tests for weather API clients with mocked responses.

This module tests the weather API clients (OpenWeatherMap and PVGIS)
using mocked HTTP responses to avoid requiring actual API keys and
network connectivity during testing.
"""

import tempfile
from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest
import pytz
import requests

from pvsolarsim.weather.api_clients import OpenWeatherMapClient, PVGISClient


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache directory before each test to avoid interference."""
    import os
    from pathlib import Path

    def clean_cache_dir(cache_dir):
        """Clean cache files from a directory."""
        if not os.path.exists(cache_dir):
            return
        for file in os.listdir(cache_dir):
            if file.startswith("pvsolarsim_cache_") or file.endswith(".pkl"):
                try:
                    os.remove(os.path.join(cache_dir, file))
                except (OSError, PermissionError):
                    pass

    # Clear both the temp directory and the user cache directory
    cache_dirs = [
        tempfile.gettempdir(),
        Path.home() / ".pvsolarsim" / "cache",
    ]

    # Clean up cache files BEFORE test
    for cache_dir in cache_dirs:
        clean_cache_dir(cache_dir)

    yield  # Run the test

    # Clean up again after test
    for cache_dir in cache_dirs:
        clean_cache_dir(cache_dir)


class TestOpenWeatherMapClient:
    """Test OpenWeatherMap API client."""

    @pytest.fixture
    def sample_api_response(self):
        """Create sample API response matching actual OpenWeatherMap OneCall API format."""
        return {
            "lat": 40.0,
            "lon": -105.0,
            "timezone": "America/Denver",
            "hourly": [
                {
                    "dt": 1704067200,  # 2024-01-01 00:00:00 UTC
                    "temp": 273.15,  # 0°C in Kelvin
                    "wind_speed": 3.0,
                    "clouds": 0,
                },
                {
                    "dt": 1704070800,  # 2024-01-01 01:00:00 UTC
                    "temp": 274.15,  # 1°C in Kelvin
                    "wind_speed": 3.5,
                    "clouds": 10,
                },
                {
                    "dt": 1704074400,  # 2024-01-01 02:00:00 UTC
                    "temp": 275.15,  # 2°C in Kelvin
                    "wind_speed": 4.0,
                    "clouds": 20,
                },
            ],
        }

    def test_client_initialization(self):
        """Test client initialization."""
        client = OpenWeatherMapClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.cache_ttl == 86400  # default
        assert client.timeout == 30  # default

    def test_client_custom_parameters(self):
        """Test client with custom parameters."""
        client = OpenWeatherMapClient(api_key="test_key", cache_ttl=3600, timeout=60)
        assert client.cache_ttl == 3600
        assert client.timeout == 60

    def test_read_success(self, sample_api_response):
        """Test successful data read from OpenWeatherMap API."""
        client = OpenWeatherMapClient(api_key="test_key")

        # Mock the session.get method directly on the client instance
        with patch.object(client.session, "get") as mock_get:
            # Mock the API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_api_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
            end = datetime(2024, 1, 1, 2, 0, 0, tzinfo=pytz.UTC)

            result = client.read(latitude=40.0, longitude=-105.0, start=start, end=end)

            # Verify result is a DataFrame
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 3  # All 3 hourly records should be included

            # Verify columns exist
            assert "temp_air" in result.columns
            assert "wind_speed" in result.columns
            assert "cloud_cover" in result.columns

            # Verify temperature conversion from Kelvin to Celsius
            assert result.iloc[0]["temp_air"] == pytest.approx(0.0, abs=0.1)
            assert result.iloc[1]["temp_air"] == pytest.approx(1.0, abs=0.1)

            # Verify cloud cover is extracted
            assert result.iloc[0]["cloud_cover"] == 0
            assert result.iloc[1]["cloud_cover"] == 10

            # Check that API was called
            assert mock_get.called

    def test_read_http_error(self):
        """Test handling of HTTP errors."""
        client = OpenWeatherMapClient(api_key="test_key")

        with patch.object(client.session, "get") as mock_get:
            # Mock HTTP error
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
            mock_get.return_value = mock_response

            start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
            end = datetime(2024, 1, 1, 23, 59, 59, tzinfo=pytz.UTC)

            with pytest.raises(ValueError, match="Failed to fetch data from OpenWeatherMap"):
                client.read(latitude=40.0, longitude=-105.0, start=start, end=end)

    def test_read_network_error(self):
        """Test handling of network errors."""
        client = OpenWeatherMapClient(api_key="test_key")

        with patch.object(client.session, "get") as mock_get:
            # Mock network error
            mock_get.side_effect = requests.ConnectionError("Network error")

            start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
            end = datetime(2024, 1, 1, 23, 59, 59, tzinfo=pytz.UTC)

            with pytest.raises(ValueError, match="Failed to fetch data from OpenWeatherMap"):
                client.read(latitude=40.0, longitude=-105.0, start=start, end=end)

    def test_read_missing_start_end(self):
        """Test that ValueError is raised when start or end is None."""
        client = OpenWeatherMapClient(api_key="test_key")

        with pytest.raises(ValueError, match="Both start and end times must be specified"):
            client.read(latitude=40.0, longitude=-105.0, start=None, end=None)

        with pytest.raises(ValueError, match="Both start and end times must be specified"):
            client.read(
                latitude=40.0,
                longitude=-105.0,
                start=datetime(2024, 1, 1, tzinfo=pytz.UTC),
                end=None,
            )

    def test_read_no_data_in_range(self):
        """Test handling when no data is in the specified time range."""
        client = OpenWeatherMapClient(api_key="test_key")

        with patch.object(client.session, "get") as mock_get:
            # Mock API response with data outside the requested range
            api_response = {
                "hourly": [
                    {
                        "dt": 1704067200 - 86400,  # One day before start
                        "temp": 273.15,
                        "wind_speed": 3.0,
                        "clouds": 0,
                    },
                ],
            }

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
            end = datetime(2024, 1, 1, 23, 59, 59, tzinfo=pytz.UTC)

            with pytest.raises(ValueError, match="No data available for the specified time range"):
                client.read(latitude=40.0, longitude=-105.0, start=start, end=end)

    def test_caching(self, sample_api_response):
        """Test that caching works correctly."""
        client = OpenWeatherMapClient(api_key="test_key", cache_ttl=3600)

        with patch.object(client.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_api_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
            end = datetime(2024, 1, 1, 2, 0, 0, tzinfo=pytz.UTC)

            # First call - should hit API
            result1 = client.read(latitude=40.0, longitude=-105.0, start=start, end=end)
            assert mock_get.call_count == 1

            # Second call with same parameters - should use cache
            result2 = client.read(latitude=40.0, longitude=-105.0, start=start, end=end)
            assert mock_get.call_count == 1  # Should not call API again

            # Results should be identical
            pd.testing.assert_frame_equal(result1, result2)


class TestPVGISClient:
    """Test PVGIS API client."""

    @pytest.fixture
    def sample_tmy_response(self):
        """Create sample PVGIS TMY response."""
        return {
            "inputs": {"location": {"latitude": 40.0, "longitude": -105.0}},
            "outputs": {
                "tmy_hourly": [
                    {
                        "time(UTC)": "20050101:0000",
                        "G(h)": 0,
                        "Gb(n)": 0,
                        "Gd(h)": 0,
                        "T2m": 0,
                        "WS10m": 3.0,
                    },
                    {
                        "time(UTC)": "20050101:0100",
                        "G(h)": 100,
                        "Gb(n)": 200,
                        "Gd(h)": 50,
                        "T2m": 1,
                        "WS10m": 3.5,
                    },
                ]
            },
        }

    def test_client_initialization(self):
        """Test PVGIS client initialization."""
        client = PVGISClient()
        assert client.cache_ttl == 604800  # default 1 week
        assert client.timeout == 60  # default

    def test_client_custom_parameters(self):
        """Test PVGIS client with custom parameters."""
        client = PVGISClient(cache_ttl=3600, timeout=120)
        assert client.cache_ttl == 3600
        assert client.timeout == 120

    def test_read_tmy_success(self, sample_tmy_response):
        """Test successful TMY data read."""
        client = PVGISClient()

        with patch.object(client.session, "get") as mock_get:
            # Mock the API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_tmy_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = client.read_tmy(latitude=40.0, longitude=-105.0)

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2

            # Verify required columns
            assert "ghi" in result.columns
            assert "dni" in result.columns
            assert "dhi" in result.columns
            assert "temp_air" in result.columns
            assert "wind_speed" in result.columns

            # Check that API was called
            assert mock_get.called

            # Verify values are correct
            assert result.iloc[0]["ghi"] == 0
            assert result.iloc[1]["ghi"] == 100

    def test_read_tmy_http_error(self):
        """Test handling of HTTP errors in TMY read."""
        client = PVGISClient()

        with patch.object(client.session, "get") as mock_get:
            # Mock HTTP error - it gets wrapped in ValueError by the client
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
            mock_get.return_value = mock_response

            # The client wraps HTTP errors in ValueError
            with pytest.raises(ValueError, match="Failed to fetch data from PVGIS"):
                client.read_tmy(latitude=40.0, longitude=-105.0)

    def test_read_tmy_invalid_json(self):
        """Test handling of invalid JSON response."""
        client = PVGISClient()

        with patch.object(client.session, "get") as mock_get:
            # Mock invalid JSON response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Should raise ValueError due to JSON parse error
            with pytest.raises(ValueError, match="Failed to fetch data from PVGIS|Invalid JSON"):
                client.read_tmy(latitude=40.0, longitude=-105.0)

    def test_read_tmy_invalid_format(self):
        """Test handling of response with invalid format."""
        client = PVGISClient()

        with patch.object(client.session, "get") as mock_get:
            # Mock response without required fields
            invalid_response = {"inputs": {}, "outputs": {}}  # Missing 'tmy_hourly'

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = invalid_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Use a unique location to avoid cache hits
            with pytest.raises(ValueError, match="Invalid PVGIS response format"):
                client.read_tmy(latitude=40.123, longitude=-105.456)

    def test_read_calls_read_tmy(self, sample_tmy_response):
        """Test that read() method delegates to read_tmy() for PVGIS."""
        client = PVGISClient()

        with patch.object(client.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_tmy_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = client.read(latitude=40.0, longitude=-105.0)

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2

    def test_pvgis_caching(self, sample_tmy_response):
        """Test that PVGIS caching works correctly."""
        client = PVGISClient(cache_ttl=3600)

        with patch.object(client.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_tmy_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Use unique coordinates to avoid cache hits from other tests
            # First call - should hit API
            result1 = client.read_tmy(latitude=41.234, longitude=-106.789)
            assert mock_get.call_count == 1

            # Second call with same parameters - should use cache
            result2 = client.read_tmy(latitude=41.234, longitude=-106.789)
            assert mock_get.call_count == 1  # Should not call API again

            # Results should be identical
            pd.testing.assert_frame_equal(result1, result2)


class TestWeatherAPIIntegration:
    """Test weather API integration features."""

    def test_retry_logic(self):
        """Test that retry configuration is properly set up."""
        client = OpenWeatherMapClient(api_key="test_key")

        # Verify that the session has retry adapters configured
        assert hasattr(client.session, "adapters")

        # Check HTTP and HTTPS adapters exist
        http_adapter = client.session.get_adapter("http://test.com")
        https_adapter = client.session.get_adapter("https://test.com")

        assert http_adapter is not None
        assert https_adapter is not None

        # Verify max_retries is configured (should be Retry object)
        assert hasattr(http_adapter, "max_retries")
        assert http_adapter.max_retries.total == 3  # As configured in _create_session

    def test_session_creation(self):
        """Test that HTTP session is created with retry configuration."""
        client = OpenWeatherMapClient(api_key="test_key")

        # Verify session exists
        assert hasattr(client, "session")
        assert isinstance(client.session, requests.Session)

        # Verify adapters are mounted
        assert "http://" in client.session.adapters
        assert "https://" in client.session.adapters

    def test_pvgis_session_creation(self):
        """Test that PVGIS client also has proper session setup."""
        client = PVGISClient()

        # Verify session exists
        assert hasattr(client, "session")
        assert isinstance(client.session, requests.Session)

    def test_parameter_validation(self):
        """Test that proper parameters are sent to the API."""
        client = OpenWeatherMapClient(api_key="test_api_key_123")

        with patch.object(client.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "hourly": [
                    {
                        "dt": 1704067200,
                        "temp": 273.15,
                        "wind_speed": 3.0,
                        "clouds": 0,
                    }
                ]
            }
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
            end = datetime(2024, 1, 1, 1, 0, 0, tzinfo=pytz.UTC)

            client.read(latitude=40.5, longitude=-105.3, start=start, end=end)

            # Verify the API was called with correct parameters
            assert mock_get.called
            call_args = mock_get.call_args

            # Check that params include API key and lat/lon
            params = call_args[1].get("params", {})
            assert "appid" in params
            assert params["appid"] == "test_api_key_123"
            assert "lat" in params
            assert "lon" in params
