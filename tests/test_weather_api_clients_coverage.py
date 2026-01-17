"""Additional tests for weather API clients to improve coverage."""

from datetime import datetime

import pandas as pd
import pytest
import pytz
import requests

from pvsolarsim.weather.api_clients import OpenWeatherMapClient, PVGISClient


class TestOpenWeatherMapClientBasics:
    """Test OpenWeatherMap client basic functionality."""

    def test_client_initialization(self):
        """Test client initialization with required parameters."""
        client = OpenWeatherMapClient(api_key="test_key_123")
        assert client.api_key == "test_key_123"
        assert client.cache_ttl == 86400
        assert client.timeout == 30
        assert client.session is not None
        assert client.cache is not None

    def test_client_custom_parameters(self):
        """Test client with custom cache and timeout."""
        client = OpenWeatherMapClient(
            api_key="custom_key",
            cache_ttl=3600,
            timeout=60
        )
        assert client.cache_ttl == 3600
        assert client.timeout == 60

    def test_session_creation(self):
        """Test that session is created with retry logic."""
        client = OpenWeatherMapClient(api_key="test_key")
        session = client._create_session()

        assert isinstance(session, requests.Session)
        # Check that adapters are mounted
        assert "http://" in session.adapters
        assert "https://" in session.adapters




class TestPVGISClientBasics:
    """Test PVGIS client basic functionality."""

    def test_client_initialization_defaults(self):
        """Test PVGIS client with default parameters."""
        client = PVGISClient()
        assert client.cache_ttl == 604800  # 1 week
        assert client.timeout == 60
        assert client.session is not None

    def test_client_custom_parameters(self):
        """Test PVGIS client with custom parameters."""
        client = PVGISClient(cache_ttl=3600, timeout=120)
        assert client.cache_ttl == 3600
        assert client.timeout == 120

    def test_session_creation(self):
        """Test that session is created properly."""
        client = PVGISClient()
        session = client._create_session()

        assert isinstance(session, requests.Session)




class TestOpenWeatherMapParsing:
    """Test OpenWeatherMap response parsing."""

    def test_parse_response_basic(self):
        """Test parsing a valid response."""
        client = OpenWeatherMapClient(api_key="test_key")

        start = pytz.UTC.localize(datetime(2024, 1, 1, 0, 0))
        end = pytz.UTC.localize(datetime(2024, 1, 1, 23, 59))

        # Mock response format matching actual OpenWeatherMap OneCall API
        response_data = {
            "hourly": [
                {
                    "dt": 1704067200,  # 2024-01-01 00:00:00 UTC
                    "temp": 273.15,
                    "wind_speed": 3.0,
                    "clouds": 20,
                }
            ]
        }

        df = client._parse_response(response_data, start, end)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert "temp_air" in df.columns
        assert "wind_speed" in df.columns
        assert "cloud_cover" in df.columns

    def test_parse_response_temperature_conversion(self):
        """Test that temperature is converted from Kelvin to Celsius."""
        client = OpenWeatherMapClient(api_key="test_key")

        start = pytz.UTC.localize(datetime(2024, 1, 1, 0, 0))
        end = pytz.UTC.localize(datetime(2024, 1, 1, 23, 59))

        response_data = {
            "hourly": [
                {
                    "dt": 1704067200,
                    "temp": 298.15,  # 25°C in Kelvin
                    "wind_speed": 3.0,
                    "clouds": 20,
                }
            ]
        }

        df = client._parse_response(response_data, start, end)

        # Should be converted to Celsius
        assert df["temp_air"].iloc[0] == pytest.approx(25.0, abs=0.1)


class TestPVGISParsing:
    """Test PVGIS response parsing."""

    def test_parse_tmy_response(self):
        """Test parsing TMY response."""
        client = PVGISClient()

        tmy_data = {
            "outputs": {
                "tmy_hourly": [
                    {
                        "time(UTC)": "20050101:0000",
                        "G(h)": 0,
                        "Gb(n)": 0,
                        "Gd(h)": 0,
                        "T2m": 0.0,
                        "WS10m": 3.0,
                    },
                    {
                        "time(UTC)": "20050101:0100",
                        "G(h)": 100,
                        "Gb(n)": 200,
                        "Gd(h)": 50,
                        "T2m": 1.0,
                        "WS10m": 3.5,
                    },
                ]
            }
        }

        df = client._parse_tmy_response(tmy_data)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "ghi" in df.columns
        assert "dni" in df.columns
        assert "dhi" in df.columns
        assert "temp_air" in df.columns
        assert "wind_speed" in df.columns




class TestWeatherCacheIntegration:
    """Test that cache is properly used."""

    def test_openweathermap_uses_cache(self):
        """Test that OpenWeatherMap client uses cache."""
        client = OpenWeatherMapClient(api_key="test_key", cache_ttl=3600)

        # Cache should be initialized
        assert client.cache is not None
        assert client.cache.ttl == 3600

    def test_pvgis_uses_cache(self):
        """Test that PVGIS client uses cache."""
        client = PVGISClient(cache_ttl=7200)

        # Cache should be initialized
        assert client.cache is not None
        assert client.cache.ttl == 7200
