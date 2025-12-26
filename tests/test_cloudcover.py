"""Tests for cloud cover modeling."""

import numpy as np
import pytest

from pvsolarsim.atmosphere.cloudcover import (
    CloudAdjustedIrradiance,
    CloudCoverModel,
    apply_cloud_cover,
    calculate_cloud_attenuation,
)


class TestCloudAttenuation:
    """Test cloud attenuation calculations."""

    def test_no_clouds(self):
        """Test attenuation with no clouds (should be 1.0)."""
        factor = calculate_cloud_attenuation(0, 45.0)
        assert factor == pytest.approx(1.0, abs=0.001)

    def test_full_clouds(self):
        """Test attenuation with 100% cloud cover."""
        factor = calculate_cloud_attenuation(100, 45.0)
        assert 0 < factor < 1.0  # Should reduce irradiance
        assert factor < 0.6  # Significant reduction

    def test_partial_clouds(self):
        """Test attenuation with partial cloud cover."""
        factor = calculate_cloud_attenuation(50, 45.0)
        assert 0 < factor < 1.0
        assert factor > calculate_cloud_attenuation(100, 45.0)

    def test_percentage_input(self):
        """Test that percentage input (0-100) works."""
        factor1 = calculate_cloud_attenuation(50, 45.0)
        factor2 = calculate_cloud_attenuation(0.5, 45.0)
        assert factor1 == pytest.approx(factor2, abs=0.001)

    def test_array_input(self):
        """Test vectorized calculation with arrays."""
        cloud = np.array([0, 25, 50, 75, 100])
        elevation = np.full(5, 45.0)
        factors = calculate_cloud_attenuation(cloud, elevation)

        assert len(factors) == 5
        assert factors[0] == pytest.approx(1.0, abs=0.001)  # No clouds
        assert factors[-1] < factors[0]  # Full clouds < no clouds
        assert all(factors[i] >= factors[i + 1] for i in range(4))  # Monotonic

    def test_elevation_effect(self):
        """Test that solar elevation affects attenuation."""
        factor_low = calculate_cloud_attenuation(50, 15.0)
        factor_high = calculate_cloud_attenuation(50, 75.0)

        # Higher elevation should have better transmission through clouds
        assert factor_high > factor_low

    def test_invalid_cloud_cover(self):
        """Test error handling for invalid cloud cover."""
        with pytest.raises(ValueError, match="Cloud cover must be"):
            calculate_cloud_attenuation(-10, 45.0)

        with pytest.raises(ValueError, match="Cloud cover must be"):
            calculate_cloud_attenuation(110, 45.0)

        with pytest.raises(ValueError, match="ambiguous"):
            calculate_cloud_attenuation(1.5, 45.0)


class TestCloudModels:
    """Test different cloud cover models."""

    def test_campbell_norman_model(self):
        """Test Campbell-Norman model."""
        factor = calculate_cloud_attenuation(50, 45.0, model=CloudCoverModel.CAMPBELL_NORMAN)
        assert 0 < factor < 1.0

    def test_simple_linear_model(self):
        """Test simple linear model."""
        factor = calculate_cloud_attenuation(50, 45.0, model=CloudCoverModel.SIMPLE_LINEAR)
        assert factor == pytest.approx(0.625, abs=0.001)  # 1 - 0.75 * 0.5

    def test_kasten_czeplak_model(self):
        """Test Kasten-Czeplak model."""
        factor = calculate_cloud_attenuation(50, 45.0, model=CloudCoverModel.KASTEN_CZEPLAK)
        assert 0 < factor < 1.0

    def test_model_string_input(self):
        """Test that model can be specified as string."""
        factor1 = calculate_cloud_attenuation(
            50, 45.0, model=CloudCoverModel.CAMPBELL_NORMAN
        )
        factor2 = calculate_cloud_attenuation(50, 45.0, model="campbell_norman")
        assert factor1 == pytest.approx(factor2, abs=0.001)

    def test_invalid_model(self):
        """Test error handling for invalid model."""
        with pytest.raises(ValueError, match="Invalid cloud cover model"):
            calculate_cloud_attenuation(50, 45.0, model="invalid_model")

    def test_models_comparison(self):
        """Compare different models for consistency."""
        cloud_cover = 50
        elevation = 45.0

        campbell = calculate_cloud_attenuation(
            cloud_cover, elevation, model=CloudCoverModel.CAMPBELL_NORMAN
        )
        simple = calculate_cloud_attenuation(
            cloud_cover, elevation, model=CloudCoverModel.SIMPLE_LINEAR
        )
        kasten = calculate_cloud_attenuation(
            cloud_cover, elevation, model=CloudCoverModel.KASTEN_CZEPLAK
        )

        # All should be in reasonable range
        assert all(0 < f < 1 for f in [campbell, simple, kasten])

        # Models should give different but similar results
        assert not campbell == simple
        assert abs(campbell - simple) < 0.3


class TestApplyCloudCover:
    """Test applying cloud cover to irradiance."""

    def test_no_clouds_no_change(self):
        """Test that 0% cloud cover doesn't change irradiance much."""
        result = apply_cloud_cover(
            ghi=800, dni=700, dhi=150, cloud_cover=0, solar_elevation=45.0
        )

        # With no clouds, DNI and DHI should be very close to input
        # GHI is recalculated from DNI*cos(zenith) + DHI so might differ slightly
        assert result.dni == pytest.approx(700, rel=0.01)
        assert result.dhi >= 150  # Can increase slightly due to scattering
        assert result.cloud_fraction == 0

    def test_full_clouds_reduces_irradiance(self):
        """Test that 100% cloud cover significantly reduces irradiance."""
        result = apply_cloud_cover(
            ghi=800, dni=700, dhi=150, cloud_cover=100, solar_elevation=45.0
        )

        # Should significantly reduce DNI and GHI
        assert result.dni < 700 * 0.5
        assert result.ghi < 800 * 0.8
        assert result.dhi > 150  # DHI should increase (scattered light)
        assert result.cloud_fraction == 1.0

    def test_partial_clouds(self):
        """Test partial cloud cover."""
        result = apply_cloud_cover(
            ghi=800, dni=700, dhi=150, cloud_cover=50, solar_elevation=45.0
        )

        assert 0 < result.dni < 700
        assert 0 < result.ghi < 800
        assert result.dhi >= 150
        assert result.cloud_fraction == 0.5

    def test_array_inputs(self):
        """Test vectorized operation with arrays."""
        ghi = np.array([800, 800, 800])
        dni = np.array([700, 700, 700])
        dhi = np.array([150, 150, 150])
        cloud_cover = np.array([0, 50, 100])
        elevation = np.full(3, 45.0)

        result = apply_cloud_cover(ghi, dni, dhi, cloud_cover, elevation)

        assert len(result.ghi) == 3
        assert result.ghi[0] > result.ghi[1] > result.ghi[2]  # Decreasing with clouds
        assert result.dni[0] > result.dni[1] > result.dni[2]

    def test_percentage_input(self):
        """Test that percentage cloud cover (0-100) works."""
        result1 = apply_cloud_cover(
            ghi=800, dni=700, dhi=150, cloud_cover=50, solar_elevation=45.0
        )
        result2 = apply_cloud_cover(
            ghi=800, dni=700, dhi=150, cloud_cover=0.5, solar_elevation=45.0
        )

        assert result1.ghi == pytest.approx(result2.ghi, abs=0.1)
        assert result1.cloud_fraction == pytest.approx(result2.cloud_fraction, abs=0.001)

    def test_different_models(self):
        """Test applying different cloud models."""
        result_campbell = apply_cloud_cover(
            ghi=800,
            dni=700,
            dhi=150,
            cloud_cover=50,
            solar_elevation=45.0,
            model=CloudCoverModel.CAMPBELL_NORMAN,
        )
        result_simple = apply_cloud_cover(
            ghi=800,
            dni=700,
            dhi=150,
            cloud_cover=50,
            solar_elevation=45.0,
            model=CloudCoverModel.SIMPLE_LINEAR,
        )

        # Different models should give different results
        assert result_campbell.ghi != pytest.approx(result_simple.ghi, abs=10)

    def test_low_elevation(self):
        """Test cloud cover at low solar elevation."""
        result = apply_cloud_cover(
            ghi=300, dni=250, dhi=100, cloud_cover=50, solar_elevation=15.0
        )

        assert 0 < result.ghi < 300
        assert 0 < result.dni < 250

    def test_high_elevation(self):
        """Test cloud cover at high solar elevation."""
        result = apply_cloud_cover(
            ghi=900, dni=800, dhi=150, cloud_cover=50, solar_elevation=75.0
        )

        assert 0 < result.ghi < 900
        assert 0 < result.dni < 800

    def test_dataclass_attributes(self):
        """Test CloudAdjustedIrradiance dataclass."""
        result = apply_cloud_cover(
            ghi=800, dni=700, dhi=150, cloud_cover=50, solar_elevation=45.0
        )

        assert isinstance(result, CloudAdjustedIrradiance)
        assert hasattr(result, "ghi")
        assert hasattr(result, "dni")
        assert hasattr(result, "dhi")
        assert hasattr(result, "cloud_fraction")


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_irradiance(self):
        """Test with zero irradiance (nighttime)."""
        result = apply_cloud_cover(
            ghi=0, dni=0, dhi=0, cloud_cover=50, solar_elevation=0
        )

        assert result.ghi == 0
        assert result.dni == 0

    def test_very_low_elevation(self):
        """Test with very low solar elevation."""
        factor = calculate_cloud_attenuation(50, 1.0)
        assert 0 < factor < 1.0

    def test_mixed_array_scalar(self):
        """Test with mix of array and scalar inputs."""
        # When mixing arrays and scalars, result dimensions depend on which inputs are arrays
        # Most common case: all irradiance components are arrays
        ghi = np.array([800, 900, 1000])
        dni = np.array([700, 800, 900])
        dhi = np.array([150, 160, 170])
        result = apply_cloud_cover(
            ghi=ghi, dni=dni, dhi=dhi, cloud_cover=50, solar_elevation=45.0
        )

        assert isinstance(result.ghi, np.ndarray)
        assert len(result.ghi) == 3
        assert isinstance(result.dni, np.ndarray)
        assert len(result.dni) == 3

    def test_scalar_output(self):
        """Test that scalar inputs produce scalar outputs."""
        result = apply_cloud_cover(
            ghi=800, dni=700, dhi=150, cloud_cover=50, solar_elevation=45.0
        )

        assert isinstance(result.ghi, float)
        assert isinstance(result.dni, float)
        assert isinstance(result.dhi, float)

    def test_consistency(self):
        """Test that GHI is consistent with DNI and DHI components."""
        elevation = 45.0
        zenith = 90 - elevation

        result = apply_cloud_cover(
            ghi=800, dni=700, dhi=150, cloud_cover=50, solar_elevation=elevation
        )

        # GHI should approximately equal DNI * cos(zenith) + DHI
        expected_ghi = result.dni * np.cos(np.radians(zenith)) + result.dhi
        assert result.ghi == pytest.approx(expected_ghi, rel=0.01)
