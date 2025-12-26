"""Tests for weather data caching."""

import tempfile
import time
from pathlib import Path

import pandas as pd
import pytest

from pvsolarsim.weather.cache import WeatherCache


def test_cache_set_and_get():
    """Test basic cache set and get operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = WeatherCache(cache_dir=Path(tmpdir), ttl=3600)

        # Create test data
        timestamps = pd.date_range("2025-01-01", periods=24, freq="H", tz="UTC")
        data = pd.DataFrame(
            {
                "ghi": [100.0] * 24,
                "temp_air": [25.0] * 24,
            },
            index=timestamps,
        )

        # Set cache
        cache.set("test_key", data)

        # Get cache
        cached_data = cache.get("test_key")

        assert cached_data is not None
        assert isinstance(cached_data, pd.DataFrame)
        assert len(cached_data) == 24
        pd.testing.assert_frame_equal(cached_data, data)


def test_cache_expiration():
    """Test that cache expires after TTL."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = WeatherCache(cache_dir=Path(tmpdir), ttl=1)  # 1 second TTL

        timestamps = pd.date_range("2025-01-01", periods=24, freq="H", tz="UTC")
        data = pd.DataFrame(
            {
                "ghi": [100.0] * 24,
                "temp_air": [25.0] * 24,
            },
            index=timestamps,
        )

        cache.set("test_key", data)

        # Should be available immediately
        assert cache.get("test_key") is not None

        # Wait for expiration
        time.sleep(1.5)

        # Should be expired
        assert cache.get("test_key") is None


def test_cache_missing_key():
    """Test getting non-existent cache key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = WeatherCache(cache_dir=Path(tmpdir), ttl=3600)

        result = cache.get("nonexistent_key")
        assert result is None


def test_cache_clear():
    """Test clearing all cache."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = WeatherCache(cache_dir=Path(tmpdir), ttl=3600)

        timestamps = pd.date_range("2025-01-01", periods=24, freq="H", tz="UTC")
        data = pd.DataFrame(
            {
                "ghi": [100.0] * 24,
                "temp_air": [25.0] * 24,
            },
            index=timestamps,
        )

        # Set multiple cache entries
        cache.set("key1", data)
        cache.set("key2", data)

        # Verify they exist
        assert cache.get("key1") is not None
        assert cache.get("key2") is not None

        # Clear cache
        cache.clear()

        # Should be gone
        assert cache.get("key1") is None
        assert cache.get("key2") is None


def test_cache_clear_expired():
    """Test clearing only expired entries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = WeatherCache(cache_dir=Path(tmpdir), ttl=1)

        timestamps = pd.date_range("2025-01-01", periods=24, freq="H", tz="UTC")
        data = pd.DataFrame(
            {
                "ghi": [100.0] * 24,
                "temp_air": [25.0] * 24,
            },
            index=timestamps,
        )

        # Set first entry
        cache.set("old_key", data)

        # Wait a bit
        time.sleep(1.5)

        # Set second entry
        cache.set("new_key", data)

        # Clear expired
        cache.clear_expired()

        # Old should be gone, new should remain
        assert cache.get("old_key") is None
        assert cache.get("new_key") is not None


def test_cache_directory_creation():
    """Test that cache directory is created if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / "subdir" / "cache"
        assert not cache_dir.exists()

        cache = WeatherCache(cache_dir=cache_dir, ttl=3600)

        # Directory should be created
        assert cache_dir.exists()
        assert cache_dir.is_dir()


def test_cache_default_directory():
    """Test cache uses default directory if not specified."""
    cache = WeatherCache(ttl=3600)

    # Should create in home directory
    expected_dir = Path.home() / ".pvsolarsim" / "cache"
    assert cache.cache_dir == expected_dir
