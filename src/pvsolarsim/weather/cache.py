"""Caching utilities for weather data.

This module provides a simple file-based caching system for weather data
to reduce API calls and improve performance.
"""

import hashlib
import pickle
import time
from pathlib import Path
from typing import Optional

import pandas as pd


class WeatherCache:
    """Simple file-based cache for weather data.

    Stores weather data in pickle files with TTL-based expiration.

    Parameters
    ----------
    cache_dir : str or Path, optional
        Directory for cache files (default: ~/.pvsolarsim/cache)
    ttl : int, optional
        Time-to-live in seconds (default: 86400 = 24 hours)

    Examples
    --------
    >>> cache = WeatherCache(ttl=3600)  # 1 hour TTL
    >>> cache.set('key', weather_data)
    >>> data = cache.get('key')
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        ttl: int = 86400,
    ):
        if cache_dir is None:
            cache_dir = Path.home() / ".pvsolarsim" / "cache"

        self.cache_dir = Path(cache_dir)
        self.ttl = ttl

        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for a given key.

        Parameters
        ----------
        key : str
            Cache key

        Returns
        -------
        Path
            Path to cache file
        """
        # Hash the key to create a safe filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.pkl"

    def get(self, key: str) -> Optional[pd.DataFrame]:
        """Retrieve data from cache.

        Parameters
        ----------
        key : str
            Cache key

        Returns
        -------
        pd.DataFrame or None
            Cached data if found and not expired, None otherwise
        """
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, "rb") as f:
                cache_data = pickle.load(f)

            # Check if cache has expired
            if time.time() - cache_data["timestamp"] > self.ttl:
                # Cache expired, delete file
                cache_path.unlink()
                return None

            return cache_data["data"]

        except (pickle.PickleError, KeyError, OSError):
            # Cache file is corrupted or unreadable, delete it
            if cache_path.exists():
                cache_path.unlink()
            return None

    def set(self, key: str, data: pd.DataFrame) -> None:
        """Store data in cache.

        Parameters
        ----------
        key : str
            Cache key
        data : pd.DataFrame
            Data to cache
        """
        cache_path = self._get_cache_path(key)

        cache_data = {
            "timestamp": time.time(),
            "data": data,
        }

        try:
            with open(cache_path, "wb") as f:
                pickle.dump(cache_data, f)
        except (pickle.PickleError, OSError):
            # Silently fail if we can't write to cache
            # (e.g., disk full, permissions issue)
            pass

    def clear(self) -> None:
        """Clear all cached data."""
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                cache_file.unlink()
            except OSError:
                pass

    def clear_expired(self) -> None:
        """Remove expired cache entries."""
        current_time = time.time()

        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                with open(cache_file, "rb") as f:
                    cache_data = pickle.load(f)

                if current_time - cache_data["timestamp"] > self.ttl:
                    cache_file.unlink()

            except (pickle.PickleError, KeyError, OSError):
                # Corrupted file, delete it
                try:
                    cache_file.unlink()
                except OSError:
                    pass
