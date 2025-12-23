"""Tests for Location model."""

import pytest

from pvsolarsim.core.location import Location


def test_location_valid():
    """Test valid location creation."""
    loc = Location(latitude=49.8, longitude=15.5, altitude=300, timezone="Europe/Prague")
    assert loc.latitude == 49.8
    assert loc.longitude == 15.5
    assert loc.altitude == 300
    assert loc.timezone == "Europe/Prague"


def test_location_invalid_latitude():
    """Test invalid latitude raises error."""
    with pytest.raises(ValueError, match="Latitude must be between"):
        Location(latitude=91.0, longitude=15.5)

    with pytest.raises(ValueError, match="Latitude must be between"):
        Location(latitude=-91.0, longitude=15.5)


def test_location_invalid_longitude():
    """Test invalid longitude raises error."""
    with pytest.raises(ValueError, match="Longitude must be between"):
        Location(latitude=49.8, longitude=181.0)


def test_location_defaults():
    """Test default values."""
    loc = Location(latitude=49.8, longitude=15.5)
    assert loc.altitude == 0.0
    assert loc.timezone == "UTC"
