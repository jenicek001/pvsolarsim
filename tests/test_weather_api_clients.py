"""Tests for weather API clients with mocked responses."""

from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest
import pytz
import requests

from pvsolarsim.weather.api_clients import OpenWeatherMapClient, PVGISClient


class TestOpenWeatherMapClient:
    """Test OpenWeatherMap API client."""

    @pytest.fixture
    def sample_api_response(self):
        """Create sample API response."""
        return {
            "lat": 40.0,
            "lon": -105.0,
            "timezone": "America/Denver",
            "data": [
                {
                    "dt": 1704067200,  # 2024-01-01 00:00:00
                    "ghi": 0,
                    "dni": 0,
                    "dhi": 0,
                    "temp": 273.15,  # 0°C
                    "wind_speed": 3.0,
                    "clouds": 0,
                },
                {
                    "dt": 1704070800,  # 2024-01-01 01:00:00
                    "ghi": 100,
                    "dni": 200,
                    "dhi": 50,
                    "temp": 274.15,
                    "wind_speed": 3.5,
                    "clouds": 10,
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

    @patch("requests.Session.get")
    def test_read_success(self, mock_get, sample_api_response):
        """Test successful data read."""
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_api_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = OpenWeatherMapClient(api_key="test_key")
        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2024, 1, 1, 23, 59, 59, tzinfo=pytz.UTC)

        result = client.read(latitude=40.0, longitude=-105.0, start=start, end=end)

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        # Check that API was called
        assert mock_get.called

    @patch("requests.Session.get")
    def test_read_http_error(self, mock_get):
        """Test handling of HTTP errors."""
        # Mock HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        client = OpenWeatherMapClient(api_key="test_key")
        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2024, 1, 1, 23, 59, 59, tzinfo=pytz.UTC)

        with pytest.raises(requests.HTTPError):
            client.read(latitude=40.0, longitude=-105.0, start=start, end=end)

    @patch("requests.Session.get")
    def test_read_network_error(self, mock_get):
        """Test handling of network errors."""
        # Mock network error
        mock_get.side_effect = requests.ConnectionError("Network error")

        client = OpenWeatherMapClient(api_key="test_key")
        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2024, 1, 1, 23, 59, 59, tzinfo=pytz.UTC)

        with pytest.raises(requests.ConnectionError):
            client.read(latitude=40.0, longitude=-105.0, start=start, end=end)


class TestPVGISClient:
    """Test PVGIS API client."""

    @pytest.fixture
    def sample_tmy_response(self):
        """Create sample PVGIS TMY response."""
        return {
            "inputs": {
                "location": {"latitude": 40.0, "longitude": -105.0}
            },
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

    @patch("requests.Session.get")
    def test_read_tmy_success(self, mock_get, sample_tmy_response):
        """Test successful TMY data read."""
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_tmy_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = PVGISClient()
        result = client.read_tmy(latitude=40.0, longitude=-105.0)

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        # Check that API was called
        assert mock_get.called

    @patch("requests.Session.get")
    def test_read_tmy_http_error(self, mock_get):
        """Test handling of HTTP errors in TMY read."""
        # Mock HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
        mock_get.return_value = mock_response

        client = PVGISClient()

        with pytest.raises(requests.HTTPError):
            client.read_tmy(latitude=40.0, longitude=-105.0)

    @patch("requests.Session.get")
    def test_read_tmy_invalid_json(self, mock_get):
        """Test handling of invalid JSON response."""
        # Mock invalid JSON response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = PVGISClient()

        with pytest.raises(ValueError):
            client.read_tmy(latitude=40.0, longitude=-105.0)

    @patch("requests.Session.get")
    def test_read_hourly_success(self, mock_get):
        """Test successful hourly data read."""
        # Mock hourly data response
        hourly_response = {
            "inputs": {"location": {"latitude": 40.0, "longitude": -105.0}},
            "outputs": {
                "hourly": [
                    {
                        "time": "20240101:0000",
                        "G(i)": 0,
                        "Gb(i)": 0,
                        "Gd(i)": 0,
                        "T2m": 0,
                        "WS10m": 3.0,
                    },
                    {
                        "time": "20240101:0100",
                        "G(i)": 100,
                        "Gb(i)": 200,
                        "Gd(i)": 50,
                        "T2m": 1,
                        "WS10m": 3.5,
                    },
                ]
            },
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = hourly_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = PVGISClient()
        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2024, 1, 1, 23, 59, 59, tzinfo=pytz.UTC)

        result = client.read(
            latitude=40.0, longitude=-105.0, start=start, end=end
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        # Check that API was called
        assert mock_get.called


class TestWeatherAPIIntegration:
    """Test weather API integration features."""

    @patch("requests.Session.get")
    def test_retry_logic(self, mock_get):
        """Test that retry logic works for transient errors."""
        # First call fails with 503, second succeeds
        mock_response_fail = Mock()
        mock_response_fail.raise_for_status.side_effect = requests.HTTPError("503 Service Unavailable")
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            "lat": 40.0,
            "lon": -105.0,
            "data": [],
        }
        mock_response_success.raise_for_status = Mock()

        # First call fails, subsequent calls succeed
        mock_get.side_effect = [mock_response_fail, mock_response_success]

        client = OpenWeatherMapClient(api_key="test_key")
        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2024, 1, 1, 23, 59, 59, tzinfo=pytz.UTC)

        # Should succeed after retry
        result = client.read(latitude=40.0, longitude=-105.0, start=start, end=end)
        assert isinstance(result, pd.DataFrame)
        # Check that API was called multiple times
        assert mock_get.call_count >= 1

    def test_cache_key_generation(self):
        """Test that cache keys are generated correctly."""
        client = OpenWeatherMapClient(api_key="test_key")
        
        # Generate cache keys for same parameters - should be identical
        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2024, 1, 1, 23, 59, 59, tzinfo=pytz.UTC)
        
        key1 = client._get_cache_key(40.0, -105.0, start, end)
        key2 = client._get_cache_key(40.0, -105.0, start, end)
        
        assert key1 == key2
        
        # Different parameters should give different keys
        key3 = client._get_cache_key(41.0, -105.0, start, end)
        assert key1 != key3
