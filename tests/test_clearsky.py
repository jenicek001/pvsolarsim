"""Tests for atmospheric clear-sky models."""

import pytest

from pvsolarsim.atmosphere import (
    ClearSkyModel,
    IrradianceComponents,
    calculate_clearsky_irradiance,
)


class TestIrradianceComponents:
    """Test suite for IrradianceComponents dataclass."""

    def test_irradiance_components_creation(self):
        """Test IrradianceComponents dataclass."""
        irr = IrradianceComponents(ghi=800.0, dni=700.0, dhi=100.0)

        assert irr.ghi == 800.0
        assert irr.dni == 700.0
        assert irr.dhi == 100.0


class TestClearSkyIrradiance:
    """Test suite for clear-sky irradiance calculations."""

    def test_clearsky_basic_ineichen(self):
        """Test basic clear-sky calculation with Ineichen model."""
        irr = calculate_clearsky_irradiance(
            apparent_elevation=45.0,
            latitude=49.8,
            longitude=15.5,
            altitude=300,
            model="ineichen",
            linke_turbidity=3.0,
        )

        # At 45° elevation, expect substantial irradiance
        assert irr.ghi > 500, f"Expected GHI > 500 W/m², got {irr.ghi}"
        assert irr.dni > 400, f"Expected DNI > 400 W/m², got {irr.dni}"
        assert irr.dhi > 0, f"Expected DHI > 0 W/m², got {irr.dhi}"

        # GHI should be roughly DNI*sin(elevation) + DHI
        # This is approximate due to ground reflection and geometry
        assert irr.ghi <= irr.dni + irr.dhi + 50  # Allow some margin

    def test_clearsky_simplified_solis(self):
        """Test clear-sky calculation with Simplified Solis model."""
        irr = calculate_clearsky_irradiance(
            apparent_elevation=60.0,
            latitude=40.0,
            longitude=-105.0,
            altitude=1655,
            model="simplified_solis",
        )

        # At 60° elevation (high sun), expect high irradiance
        assert irr.ghi > 700, f"Expected GHI > 700 W/m², got {irr.ghi}"
        assert irr.dni > 600, f"Expected DNI > 600 W/m², got {irr.dni}"
        assert irr.dhi > 0, f"Expected DHI > 0 W/m², got {irr.dhi}"

    def test_clearsky_low_elevation(self):
        """Test clear-sky at low solar elevation."""
        irr = calculate_clearsky_irradiance(
            apparent_elevation=10.0,
            latitude=49.8,
            longitude=15.5,
            altitude=300,
            model="ineichen",
        )

        # At low elevation, irradiance should be lower
        assert irr.ghi < 500, f"Expected GHI < 500 W/m² at low elevation, got {irr.ghi}"
        assert irr.dni >= 0
        assert irr.dhi >= 0

    def test_clearsky_sun_below_horizon(self):
        """Test that negative elevation (sun below horizon) gives zero irradiance."""
        irr = calculate_clearsky_irradiance(
            apparent_elevation=-10.0,
            latitude=49.8,
            longitude=15.5,
            altitude=300,
            model="ineichen",
        )

        assert irr.ghi == 0.0
        assert irr.dni == 0.0
        assert irr.dhi == 0.0

    def test_clearsky_different_turbidity(self):
        """Test that different turbidity values affect irradiance."""
        irr_clear = calculate_clearsky_irradiance(
            apparent_elevation=45.0,
            latitude=49.8,
            longitude=15.5,
            altitude=300,
            model="ineichen",
            linke_turbidity=2.0,  # Very clear
        )

        irr_turbid = calculate_clearsky_irradiance(
            apparent_elevation=45.0,
            latitude=49.8,
            longitude=15.5,
            altitude=300,
            model="ineichen",
            linke_turbidity=5.0,  # Turbid/polluted
        )

        # Clear sky should have higher irradiance
        assert irr_clear.ghi > irr_turbid.ghi
        assert irr_clear.dni > irr_turbid.dni

    def test_clearsky_altitude_effect(self):
        """Test that altitude affects irradiance (less atmosphere at higher altitude)."""
        irr_sea_level = calculate_clearsky_irradiance(
            apparent_elevation=45.0,
            latitude=40.0,
            longitude=-105.0,
            altitude=0,
            model="ineichen",
        )

        irr_high_alt = calculate_clearsky_irradiance(
            apparent_elevation=45.0,
            latitude=40.0,
            longitude=-105.0,
            altitude=3000,  # Mountain elevation
            model="ineichen",
        )

        # Higher altitude should have slightly higher irradiance (less atmosphere)
        assert irr_high_alt.ghi > irr_sea_level.ghi

    def test_clearsky_model_enum(self):
        """Test using ClearSkyModel enum."""
        irr = calculate_clearsky_irradiance(
            apparent_elevation=45.0,
            latitude=49.8,
            longitude=15.5,
            altitude=300,
            model=ClearSkyModel.INEICHEN,
        )

        assert irr.ghi > 0
        assert irr.dni > 0
        assert irr.dhi > 0

    def test_clearsky_invalid_model(self):
        """Test that invalid model raises error."""
        with pytest.raises(ValueError, match="Invalid clear-sky model"):
            calculate_clearsky_irradiance(
                apparent_elevation=45.0,
                latitude=49.8,
                longitude=15.5,
                altitude=300,
                model="invalid_model",
            )

    @pytest.mark.parametrize(
        "elevation,expected_ghi_range",
        [
            (0, (0, 50)),  # Sunrise/sunset
            (30, (400, 800)),  # Low sun
            (60, (700, 1100)),  # High sun
            (90, (900, 1400)),  # Overhead (theoretical)
        ],
    )
    def test_clearsky_elevation_dependency(self, elevation, expected_ghi_range):
        """Test that GHI increases with solar elevation."""
        irr = calculate_clearsky_irradiance(
            apparent_elevation=elevation,
            latitude=0,  # Equator
            longitude=0,
            altitude=0,
            model="ineichen",
            linke_turbidity=3.0,
        )

        min_ghi, max_ghi = expected_ghi_range
        assert (
            min_ghi <= irr.ghi <= max_ghi
        ), f"At {elevation}° elevation, expected GHI in {expected_ghi_range}, got {irr.ghi}"
