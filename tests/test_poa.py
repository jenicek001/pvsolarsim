"""
Tests for plane-of-array (POA) irradiance calculations.
"""

import pytest

from pvsolarsim.irradiance import (
    POAComponents,
    POAIrradiance,
    calculate_poa_irradiance,
)
from pvsolarsim.irradiance.poa import (
    DiffuseModel,
    IAMModel,
    calculate_aoi,
)


class TestAOI:
    """Tests for angle of incidence calculations."""

    def test_aoi_perpendicular_sun(self):
        """Test AOI when sun is perpendicular to south-facing panel.

        Note: For a 35° tilt panel with sun at 35° elevation, AOI is NOT 0°.
        The AOI depends on both solar elevation and azimuth alignment.
        Using spherical geometry: AOI ≈ 20° when sun is directly south at 35° elevation.
        """
        # 35° tilt south-facing panel, sun at 35° elevation from south
        aoi = calculate_aoi(
            surface_tilt=35.0,
            surface_azimuth=180.0,
            solar_zenith=55.0,  # 35° elevation
            solar_azimuth=180.0,
        )
        # AOI should be around 20° (calculated via spherical geometry)
        assert aoi == pytest.approx(20.0, abs=1.0)

    def test_aoi_horizontal_panel(self):
        """Test AOI for horizontal panel (tilt = 0)."""
        # Horizontal panel, sun at 45° elevation
        aoi = calculate_aoi(
            surface_tilt=0.0,
            surface_azimuth=180.0,
            solar_zenith=45.0,
            solar_azimuth=180.0,
        )
        # AOI should equal solar zenith for horizontal panels
        assert aoi == pytest.approx(45.0, abs=0.1)

    def test_aoi_vertical_panel(self):
        """Test AOI for vertical panel (tilt = 90)."""
        # Vertical south-facing panel, sun at 45° elevation from south
        aoi = calculate_aoi(
            surface_tilt=90.0,
            surface_azimuth=180.0,
            solar_zenith=45.0,
            solar_azimuth=180.0,
        )
        # AOI should be 45° (90° - 45° elevation)
        assert aoi == pytest.approx(45.0, abs=0.5)

    def test_aoi_sun_behind_panel(self):
        """Test AOI when sun is behind the panel.

        For a south-facing 35° tilted panel with sun from the north,
        the sun vector and panel normal vector form an angle of ~80°.
        This is calculated using:
        cos(AOI) = cos(zenith)·cos(tilt) + sin(zenith)·sin(tilt)·cos(azimuth_diff)
        where azimuth_diff = 180° (sun from north, panel faces south).
        """
        # South-facing panel, sun from north
        aoi = calculate_aoi(
            surface_tilt=35.0,
            surface_azimuth=180.0,
            solar_zenith=45.0,
            solar_azimuth=0.0,  # North
        )
        # AOI should be ~80° (sun illuminates back of panel at grazing angle)
        assert aoi == pytest.approx(80.0, abs=1.0)


class TestPOAComponents:
    """Tests for POAComponents dataclass."""

    def test_poa_components_creation(self):
        """Test creating POAComponents."""
        components = POAComponents(
            poa_direct=600.0, poa_diffuse=100.0, poa_ground=50.0, poa_global=750.0
        )
        assert components.poa_direct == 600.0
        assert components.poa_diffuse == 100.0
        assert components.poa_ground == 50.0
        assert components.poa_global == 750.0


class TestPOAIrradiance:
    """Tests for POAIrradiance class."""

    def test_poa_calculation_basic(self):
        """Test basic POA calculation with default models."""
        poa_calc = POAIrradiance()
        components = poa_calc.calculate(
            surface_tilt=35.0,
            surface_azimuth=180.0,
            solar_zenith=45.0,
            solar_azimuth=180.0,
            dni=800.0,
            ghi=600.0,
            dhi=100.0,
        )

        # All components should be non-negative
        assert components.poa_direct >= 0
        assert components.poa_diffuse >= 0
        assert components.poa_ground >= 0
        assert components.poa_global >= 0

        # Global should be sum of components
        assert components.poa_global == pytest.approx(
            components.poa_direct + components.poa_diffuse + components.poa_ground,
            abs=0.1,
        )

        # POA global should be reasonable (DNI is 800, so POA shouldn't exceed ~900)
        assert components.poa_global < 1000

    def test_poa_isotropic_model(self):
        """Test POA with isotropic diffuse model."""
        poa_calc = POAIrradiance(diffuse_model="isotropic")
        components = poa_calc.calculate(
            surface_tilt=35.0,
            surface_azimuth=180.0,
            solar_zenith=45.0,
            solar_azimuth=180.0,
            dni=800.0,
            ghi=600.0,
            dhi=100.0,
        )
        assert components.poa_global > 0

    def test_poa_perez_model(self):
        """Test POA with Perez diffuse model (default)."""
        poa_calc = POAIrradiance(diffuse_model="perez")
        components = poa_calc.calculate(
            surface_tilt=35.0,
            surface_azimuth=180.0,
            solar_zenith=45.0,
            solar_azimuth=180.0,
            dni=800.0,
            ghi=600.0,
            dhi=100.0,
        )
        assert components.poa_global > 0

    def test_poa_haydavies_model(self):
        """Test POA with Hay-Davies diffuse model."""
        poa_calc = POAIrradiance(diffuse_model="haydavies")
        components = poa_calc.calculate(
            surface_tilt=35.0,
            surface_azimuth=180.0,
            solar_zenith=45.0,
            solar_azimuth=180.0,
            dni=800.0,
            ghi=600.0,
            dhi=100.0,
        )
        assert components.poa_global > 0

    def test_poa_different_albedo(self):
        """Test POA with different albedo values."""
        # Low albedo (asphalt)
        poa_low = POAIrradiance(albedo=0.1)
        components_low = poa_low.calculate(
            surface_tilt=35.0,
            surface_azimuth=180.0,
            solar_zenith=45.0,
            solar_azimuth=180.0,
            dni=800.0,
            ghi=600.0,
            dhi=100.0,
        )

        # High albedo (snow)
        poa_high = POAIrradiance(albedo=0.8)
        components_high = poa_high.calculate(
            surface_tilt=35.0,
            surface_azimuth=180.0,
            solar_zenith=45.0,
            solar_azimuth=180.0,
            dni=800.0,
            ghi=600.0,
            dhi=100.0,
        )

        # Ground-reflected component should be higher with high albedo
        assert components_high.poa_ground > components_low.poa_ground
        # Total should also be higher
        assert components_high.poa_global > components_low.poa_global

    def test_poa_horizontal_panel(self):
        """Test POA for horizontal panel (should equal GHI)."""
        poa_calc = POAIrradiance(albedo=0.0)  # No ground reflection
        components = poa_calc.calculate(
            surface_tilt=0.0,  # Horizontal
            surface_azimuth=180.0,
            solar_zenith=45.0,
            solar_azimuth=180.0,
            dni=800.0,
            ghi=600.0,
            dhi=100.0,
        )
        # For horizontal surface, POA global should approximately equal GHI
        # (with some difference due to IAM and model differences)
        assert components.poa_global == pytest.approx(600.0, rel=0.1)

    def test_poa_sun_below_horizon(self):
        """Test POA when sun is below horizon."""
        poa_calc = POAIrradiance(diffuse_model="isotropic")  # Use isotropic to avoid Perez div by zero
        components = poa_calc.calculate(
            surface_tilt=35.0,
            surface_azimuth=180.0,
            solar_zenith=95.0,  # Below horizon
            solar_azimuth=180.0,
            dni=0.0,
            ghi=0.0,
            dhi=0.0,
        )
        # All components should be zero or near-zero
        assert components.poa_direct == pytest.approx(0.0, abs=1e-6)
        assert components.poa_diffuse == pytest.approx(0.0, abs=1e-6)
        assert components.poa_ground == pytest.approx(0.0, abs=1e-6)
        assert components.poa_global == pytest.approx(0.0, abs=1e-6)

    def test_poa_high_aoi(self):
        """Test POA with high angle of incidence (grazing angle)."""
        poa_calc = POAIrradiance()
        # Sun from behind panel
        components = poa_calc.calculate(
            surface_tilt=35.0,
            surface_azimuth=180.0,  # South
            solar_zenith=45.0,
            solar_azimuth=0.0,  # North (behind panel)
            dni=800.0,
            ghi=600.0,
            dhi=100.0,
        )
        # Direct component should be very small (high AOI ~80° reduces it greatly)
        # but not zero due to IAM
        assert components.poa_direct < 100.0  # Much reduced by high AOI
        # But diffuse and ground components should still exist
        assert components.poa_diffuse > 0
        assert components.poa_global > 0

    def test_poa_invalid_tilt(self):
        """Test POA with invalid tilt angle."""
        poa_calc = POAIrradiance()
        with pytest.raises(ValueError, match="Surface tilt must be 0-90"):
            poa_calc.calculate(
                surface_tilt=100.0,  # Invalid
                surface_azimuth=180.0,
                solar_zenith=45.0,
                solar_azimuth=180.0,
                dni=800.0,
                ghi=600.0,
                dhi=100.0,
            )

    def test_poa_negative_irradiance(self):
        """Test POA with negative irradiance (should raise error)."""
        poa_calc = POAIrradiance()
        with pytest.raises(ValueError, match="Irradiance values cannot be negative"):
            poa_calc.calculate(
                surface_tilt=35.0,
                surface_azimuth=180.0,
                solar_zenith=45.0,
                solar_azimuth=180.0,
                dni=-100.0,  # Invalid
                ghi=600.0,
                dhi=100.0,
            )

    def test_invalid_diffuse_model(self):
        """Test creating POAIrradiance with invalid diffuse model."""
        with pytest.raises(ValueError, match="Invalid diffuse model"):
            POAIrradiance(diffuse_model="invalid_model")

    def test_invalid_iam_model(self):
        """Test creating POAIrradiance with invalid IAM model."""
        with pytest.raises(ValueError, match="Invalid IAM model"):
            POAIrradiance(iam_model="invalid_iam")

    def test_invalid_albedo(self):
        """Test creating POAIrradiance with invalid albedo."""
        with pytest.raises(ValueError, match="Albedo must be between 0 and 1"):
            POAIrradiance(albedo=1.5)

    def test_model_enums(self):
        """Test using model enums directly."""
        poa_calc = POAIrradiance(
            diffuse_model=DiffuseModel.PEREZ, iam_model=IAMModel.ASHRAE
        )
        components = poa_calc.calculate(
            surface_tilt=35.0,
            surface_azimuth=180.0,
            solar_zenith=45.0,
            solar_azimuth=180.0,
            dni=800.0,
            ghi=600.0,
            dhi=100.0,
        )
        assert components.poa_global > 0


class TestCalculatePOAIrradiance:
    """Tests for convenience function calculate_poa_irradiance."""

    def test_calculate_poa_basic(self):
        """Test convenience function for POA calculation."""
        components = calculate_poa_irradiance(
            surface_tilt=35.0,
            surface_azimuth=180.0,
            solar_zenith=45.0,
            solar_azimuth=180.0,
            dni=800.0,
            ghi=600.0,
            dhi=100.0,
        )
        assert components.poa_global > 0
        assert isinstance(components, POAComponents)

    def test_calculate_poa_with_options(self):
        """Test convenience function with custom models and albedo."""
        components = calculate_poa_irradiance(
            surface_tilt=35.0,
            surface_azimuth=180.0,
            solar_zenith=45.0,
            solar_azimuth=180.0,
            dni=800.0,
            ghi=600.0,
            dhi=100.0,
            diffuse_model="isotropic",
            iam_model="ashrae",
            albedo=0.5,
        )
        assert components.poa_global > 0

    def test_calculate_poa_vertical_east_facing(self):
        """Test POA for vertical east-facing panel at sunrise."""
        # Vertical east-facing panel, sun rising from east
        components = calculate_poa_irradiance(
            surface_tilt=90.0,  # Vertical
            surface_azimuth=90.0,  # East
            solar_zenith=80.0,  # Low elevation (sunrise)
            solar_azimuth=90.0,  # From east
            dni=300.0,
            ghi=150.0,
            dhi=50.0,
        )
        # Should capture some direct radiation
        assert components.poa_direct > 0
        assert components.poa_global > 0


class TestIAMModels:
    """Tests for incidence angle modifier models."""

    def test_iam_ashrae(self):
        """Test ASHRAE IAM model."""
        poa_calc = POAIrradiance(iam_model="ashrae")
        components = poa_calc.calculate(
            surface_tilt=35.0,
            surface_azimuth=180.0,
            solar_zenith=45.0,
            solar_azimuth=180.0,
            dni=800.0,
            ghi=600.0,
            dhi=100.0,
        )
        assert components.poa_global > 0

    def test_iam_physical(self):
        """Test physical (Fresnel) IAM model."""
        poa_calc = POAIrradiance(iam_model="physical")
        components = poa_calc.calculate(
            surface_tilt=35.0,
            surface_azimuth=180.0,
            solar_zenith=45.0,
            solar_azimuth=180.0,
            dni=800.0,
            ghi=600.0,
            dhi=100.0,
        )
        assert components.poa_global > 0

    def test_iam_martin_ruiz(self):
        """Test Martin-Ruiz IAM model."""
        poa_calc = POAIrradiance(iam_model="martin_ruiz")
        components = poa_calc.calculate(
            surface_tilt=35.0,
            surface_azimuth=180.0,
            solar_zenith=45.0,
            solar_azimuth=180.0,
            dni=800.0,
            ghi=600.0,
            dhi=100.0,
        )
        assert components.poa_global > 0
