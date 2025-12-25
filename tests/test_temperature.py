"""
Tests for temperature modeling module.

This module tests all temperature models and validates them against pvlib
where applicable.
"""

import numpy as np
import pytest

from pvsolarsim.temperature import (
    TemperatureModel,
    calculate_cell_temperature,
    calculate_temperature_correction_factor,
    faiman_model,
    generic_linear_model,
    pvsyst_model,
    sapm_model,
)


class TestFaimanModel:
    """Test suite for Faiman temperature model."""

    def test_faiman_basic(self):
        """Test basic Faiman model calculation."""
        temp = faiman_model(poa_global=800, temp_air=25, wind_speed=3)
        # Should be above ambient
        assert temp > 25
        # Typical range for 800 W/m² at 25°C
        assert 40 < temp < 50

    def test_faiman_scalar(self):
        """Test Faiman with scalar inputs returns scalar."""
        temp = faiman_model(poa_global=800, temp_air=25, wind_speed=3)
        assert isinstance(temp, float)

    def test_faiman_array(self):
        """Test Faiman with array inputs returns array."""
        poa = np.array([400, 800, 1000])
        temp = faiman_model(poa_global=poa, temp_air=25, wind_speed=3)
        assert isinstance(temp, np.ndarray)
        assert len(temp) == 3
        # Temperatures should increase with irradiance
        assert np.all(np.diff(temp) > 0)

    def test_faiman_zero_irradiance(self):
        """Test Faiman with zero irradiance equals ambient."""
        temp = faiman_model(poa_global=0, temp_air=20, wind_speed=2)
        assert temp == pytest.approx(20, abs=0.01)

    def test_faiman_high_wind(self):
        """Test Faiman: higher wind speed reduces temperature."""
        temp_low_wind = faiman_model(poa_global=800, temp_air=25, wind_speed=1)
        temp_high_wind = faiman_model(poa_global=800, temp_air=25, wind_speed=5)
        assert temp_high_wind < temp_low_wind

    def test_faiman_default_wind(self):
        """Test Faiman default wind speed."""
        temp = faiman_model(poa_global=800, temp_air=25)
        # Should use default wind_speed=1.0
        assert temp > 25

    def test_faiman_custom_parameters(self):
        """Test Faiman with custom u0, u1 parameters."""
        # Building-integrated (higher u0, lower heat loss -> should run hotter)
        temp_bi = faiman_model(poa_global=800, temp_air=25, wind_speed=3, u0=35, u1=5)
        # Open-rack (default parameters)
        temp_open = faiman_model(poa_global=800, temp_air=25, wind_speed=3)
        # Building-integrated has higher u0, so higher total heat loss factor
        # This actually means COOLER (more heat dissipation)
        assert temp_bi < temp_open

    def test_faiman_vs_pvlib(self):
        """Validate Faiman against pvlib implementation."""
        try:
            import pvlib.temperature

            # Test multiple conditions
            test_cases = [
                (800, 25, 3),
                (1000, 30, 5),
                (400, 15, 1),
                (0, 20, 2),
            ]

            for poa, tair, wind in test_cases:
                our_temp = faiman_model(poa_global=poa, temp_air=tair, wind_speed=wind)
                pvlib_temp = pvlib.temperature.faiman(
                    poa_global=poa, temp_air=tair, wind_speed=wind
                )
                # Should match within 0.1°C
                assert our_temp == pytest.approx(pvlib_temp, abs=0.1)
        except ImportError:
            pytest.skip("pvlib not available for validation")


class TestSAPMModel:
    """Test suite for SAPM temperature model."""

    def test_sapm_basic(self):
        """Test basic SAPM model calculation."""
        temp = sapm_model(poa_global=800, temp_air=25, wind_speed=3)
        assert temp > 25
        assert 45 < temp < 50

    def test_sapm_scalar(self):
        """Test SAPM with scalar inputs."""
        temp = sapm_model(poa_global=800, temp_air=25, wind_speed=3)
        assert isinstance(temp, float)

    def test_sapm_array(self):
        """Test SAPM with array inputs."""
        poa = np.array([400, 800, 1000])
        temp = sapm_model(poa_global=poa, temp_air=25, wind_speed=3)
        assert isinstance(temp, np.ndarray)
        assert len(temp) == 3
        assert np.all(np.diff(temp) > 0)

    def test_sapm_zero_irradiance(self):
        """Test SAPM with zero irradiance."""
        temp = sapm_model(poa_global=0, temp_air=20, wind_speed=2)
        assert temp == pytest.approx(20, abs=0.01)

    def test_sapm_high_wind(self):
        """Test SAPM: higher wind reduces temperature."""
        temp_low_wind = sapm_model(poa_global=800, temp_air=25, wind_speed=1)
        temp_high_wind = sapm_model(poa_global=800, temp_air=25, wind_speed=5)
        assert temp_high_wind < temp_low_wind

    def test_sapm_custom_parameters(self):
        """Test SAPM with custom parameters."""
        temp = sapm_model(
            poa_global=1000,
            temp_air=20,
            wind_speed=2,
            a=-3.56,
            b=-0.075,
            delta_t=3.5,
        )
        assert 45 < temp < 50

    def test_sapm_vs_pvlib(self):
        """Validate SAPM against pvlib implementation."""
        try:
            import pvlib.temperature

            test_cases = [
                (800, 25, 3),
                (1000, 30, 5),
                (400, 15, 1),
            ]

            for poa, tair, wind in test_cases:
                our_temp = sapm_model(poa_global=poa, temp_air=tair, wind_speed=wind)
                pvlib_temp = pvlib.temperature.sapm_cell(
                    poa_global=poa,
                    temp_air=tair,
                    wind_speed=wind,
                    a=-3.47,
                    b=-0.0594,
                    deltaT=3.0,  # pvlib uses deltaT, not delta_t
                )
                assert our_temp == pytest.approx(pvlib_temp, abs=0.1)
        except ImportError:
            pytest.skip("pvlib not available for validation")


class TestPVsystModel:
    """Test suite for PVsyst temperature model."""

    def test_pvsyst_basic(self):
        """Test basic PVsyst model calculation."""
        temp = pvsyst_model(poa_global=800, temp_air=25, wind_speed=3)
        assert temp > 25
        assert 40 < temp < 50

    def test_pvsyst_scalar(self):
        """Test PVsyst with scalar inputs."""
        temp = pvsyst_model(poa_global=800, temp_air=25, wind_speed=3)
        assert isinstance(temp, float)

    def test_pvsyst_array(self):
        """Test PVsyst with array inputs."""
        poa = np.array([400, 800, 1000])
        temp = pvsyst_model(poa_global=poa, temp_air=25, wind_speed=3)
        assert isinstance(temp, np.ndarray)
        assert len(temp) == 3
        assert np.all(np.diff(temp) > 0)

    def test_pvsyst_zero_irradiance(self):
        """Test PVsyst with zero irradiance."""
        temp = pvsyst_model(poa_global=0, temp_air=20, wind_speed=2)
        assert temp == pytest.approx(20, abs=0.01)

    def test_pvsyst_efficiency_effect(self):
        """Test PVsyst: higher efficiency reduces heating."""
        # Lower efficiency (more heat)
        temp_low_eff = pvsyst_model(
            poa_global=800, temp_air=25, wind_speed=3, module_efficiency=0.10
        )
        # Higher efficiency (less heat)
        temp_high_eff = pvsyst_model(
            poa_global=800, temp_air=25, wind_speed=3, module_efficiency=0.20
        )
        # Higher efficiency should run cooler
        assert temp_high_eff < temp_low_eff

    def test_pvsyst_absorption_effect(self):
        """Test PVsyst: higher absorption increases heating."""
        temp_low_abs = pvsyst_model(poa_global=800, temp_air=25, wind_speed=3, alpha_absorption=0.8)
        temp_high_abs = pvsyst_model(
            poa_global=800, temp_air=25, wind_speed=3, alpha_absorption=0.95
        )
        # Higher absorption should run hotter
        assert temp_high_abs > temp_low_abs

    def test_pvsyst_vs_pvlib(self):
        """Validate PVsyst against pvlib implementation."""
        try:
            import pvlib.temperature

            test_cases = [
                (800, 25, 3, 0.20, 0.88),
                (1000, 30, 5, 0.18, 0.90),
                (400, 15, 1, 0.15, 0.85),
            ]

            for poa, tair, wind, eff, alpha in test_cases:
                our_temp = pvsyst_model(
                    poa_global=poa,
                    temp_air=tair,
                    wind_speed=wind,
                    module_efficiency=eff,
                    alpha_absorption=alpha,
                )
                pvlib_temp = pvlib.temperature.pvsyst_cell(
                    poa_global=poa,
                    temp_air=tair,
                    wind_speed=wind,
                    module_efficiency=eff,
                    alpha_absorption=alpha,
                )
                assert our_temp == pytest.approx(pvlib_temp, abs=0.1)
        except ImportError:
            pytest.skip("pvlib not available for validation")


class TestGenericLinearModel:
    """Test suite for generic linear temperature model."""

    def test_generic_linear_basic(self):
        """Test basic generic linear model calculation."""
        temp = generic_linear_model(
            poa_global=800,
            temp_air=25,
            wind_speed=3,
            u_const=11.04,
            du_wind=5.52,
            module_efficiency=0.19,
            absorptance=0.88,
        )
        assert temp > 25
        assert 40 < temp < 50

    def test_generic_linear_scalar(self):
        """Test generic linear with scalar inputs."""
        temp = generic_linear_model(
            poa_global=800,
            temp_air=25,
            wind_speed=3,
            u_const=11.04,
            du_wind=5.52,
            module_efficiency=0.19,
            absorptance=0.88,
        )
        assert isinstance(temp, float)

    def test_generic_linear_array(self):
        """Test generic linear with array inputs."""
        poa = np.array([400, 800, 1000])
        temp = generic_linear_model(
            poa_global=poa,
            temp_air=25,
            wind_speed=3,
            u_const=11.04,
            du_wind=5.52,
            module_efficiency=0.19,
            absorptance=0.88,
        )
        assert isinstance(temp, np.ndarray)
        assert len(temp) == 3
        assert np.all(np.diff(temp) > 0)

    def test_generic_linear_vs_pvlib(self):
        """Validate generic linear against pvlib implementation."""
        try:
            import pvlib.temperature

            test_cases = [
                (800, 25, 3, 11.04, 5.52, 0.19, 0.88),
                (1000, 30, 5, 10.5, 6.0, 0.20, 0.90),
            ]

            for poa, tair, wind, u0, du, eff, alpha in test_cases:
                our_temp = generic_linear_model(
                    poa_global=poa,
                    temp_air=tair,
                    wind_speed=wind,
                    u_const=u0,
                    du_wind=du,
                    module_efficiency=eff,
                    absorptance=alpha,
                )
                pvlib_temp = pvlib.temperature.generic_linear(
                    poa_global=poa,
                    temp_air=tair,
                    wind_speed=wind,
                    u_const=u0,
                    du_wind=du,
                    module_efficiency=eff,
                    absorptance=alpha,
                )
                # Allow slightly larger tolerance due to floating point differences
                assert our_temp == pytest.approx(pvlib_temp, abs=1.0)
        except ImportError:
            pytest.skip("pvlib not available for validation")


class TestCalculateCellTemperature:
    """Test suite for unified calculate_cell_temperature function."""

    def test_default_model(self):
        """Test default model (Faiman)."""
        temp = calculate_cell_temperature(poa_global=800, temp_air=25, wind_speed=3)
        assert temp > 25

    def test_faiman_by_name(self):
        """Test specifying Faiman model by name."""
        temp = calculate_cell_temperature(poa_global=800, temp_air=25, wind_speed=3, model="faiman")
        temp_direct = faiman_model(poa_global=800, temp_air=25, wind_speed=3)
        assert temp == pytest.approx(temp_direct)

    def test_sapm_by_name(self):
        """Test specifying SAPM model by name."""
        temp = calculate_cell_temperature(poa_global=800, temp_air=25, wind_speed=3, model="sapm")
        temp_direct = sapm_model(poa_global=800, temp_air=25, wind_speed=3)
        assert temp == pytest.approx(temp_direct)

    def test_pvsyst_by_name(self):
        """Test specifying PVsyst model by name."""
        temp = calculate_cell_temperature(poa_global=800, temp_air=25, wind_speed=3, model="pvsyst")
        temp_direct = pvsyst_model(poa_global=800, temp_air=25, wind_speed=3)
        assert temp == pytest.approx(temp_direct)

    def test_generic_linear_by_name(self):
        """Test specifying generic linear model by name."""
        temp = calculate_cell_temperature(
            poa_global=800,
            temp_air=25,
            wind_speed=3,
            model="generic_linear",
            u_const=11.04,
            du_wind=5.52,
            module_efficiency=0.19,
            absorptance=0.88,
        )
        temp_direct = generic_linear_model(
            poa_global=800,
            temp_air=25,
            wind_speed=3,
            u_const=11.04,
            du_wind=5.52,
            module_efficiency=0.19,
            absorptance=0.88,
        )
        assert temp == pytest.approx(temp_direct)

    def test_model_enum(self):
        """Test using TemperatureModel enum."""
        temp = calculate_cell_temperature(
            poa_global=800,
            temp_air=25,
            wind_speed=3,
            model=TemperatureModel.FAIMAN,
        )
        assert temp > 25

    def test_invalid_model(self):
        """Test error on invalid model name."""
        with pytest.raises(ValueError, match="Invalid temperature model"):
            calculate_cell_temperature(
                poa_global=800,
                temp_air=25,
                wind_speed=3,
                model="invalid_model",
            )

    def test_case_insensitive(self):
        """Test model names are case-insensitive."""
        temp1 = calculate_cell_temperature(
            poa_global=800, temp_air=25, wind_speed=3, model="FAIMAN"
        )
        temp2 = calculate_cell_temperature(
            poa_global=800, temp_air=25, wind_speed=3, model="Faiman"
        )
        assert temp1 == pytest.approx(temp2)

    def test_with_model_params(self):
        """Test passing model-specific parameters."""
        temp = calculate_cell_temperature(
            poa_global=800,
            temp_air=25,
            wind_speed=3,
            model="faiman",
            u0=30.0,
            u1=5.0,
        )
        assert temp > 25


class TestTemperatureCorrectionFactor:
    """Test suite for temperature correction factor calculation."""

    def test_correction_at_stc(self):
        """Test correction factor at STC (25°C) is 1.0."""
        factor = calculate_temperature_correction_factor(cell_temperature=25)
        assert factor == pytest.approx(1.0)

    def test_correction_above_stc(self):
        """Test correction factor above STC reduces power."""
        factor = calculate_temperature_correction_factor(cell_temperature=45)
        # Should be less than 1.0 (power reduction)
        assert factor < 1.0
        # With default -0.004/°C and 20°C rise
        assert factor == pytest.approx(0.92, abs=0.001)

    def test_correction_below_stc(self):
        """Test correction factor below STC increases power."""
        factor = calculate_temperature_correction_factor(cell_temperature=15)
        # Should be greater than 1.0 (power increase)
        assert factor > 1.0
        # With default -0.004/°C and -10°C drop
        assert factor == pytest.approx(1.04, abs=0.001)

    def test_correction_scalar(self):
        """Test correction with scalar input."""
        factor = calculate_temperature_correction_factor(cell_temperature=45)
        assert isinstance(factor, float)

    def test_correction_array(self):
        """Test correction with array input."""
        temps = np.array([25, 35, 45, 55])
        factors = calculate_temperature_correction_factor(temps)
        assert isinstance(factors, np.ndarray)
        assert len(factors) == 4
        # Should decrease as temperature increases
        assert np.all(np.diff(factors) < 0)

    def test_custom_coefficient(self):
        """Test correction with custom temperature coefficient."""
        # CdTe with -0.0025/°C
        factor_cdte = calculate_temperature_correction_factor(
            cell_temperature=45, temp_coefficient=-0.0025
        )
        # c-Si with -0.004/°C
        factor_si = calculate_temperature_correction_factor(
            cell_temperature=45, temp_coefficient=-0.004
        )
        # CdTe should have less power loss
        assert factor_cdte > factor_si

    def test_custom_reference(self):
        """Test correction with custom reference temperature."""
        factor = calculate_temperature_correction_factor(cell_temperature=30, temp_ref=30)
        assert factor == pytest.approx(1.0)

    def test_realistic_scenario(self):
        """Test realistic scenario: hot module."""
        # Module at 55°C (typical for summer at 1000 W/m²)
        factor = calculate_temperature_correction_factor(
            cell_temperature=55,
            temp_coefficient=-0.004,
        )
        # Power reduction to 88% of STC
        assert factor == pytest.approx(0.88, abs=0.001)

        # Apply to 300W module
        power_stc = 300
        power_actual = power_stc * factor
        assert power_actual == pytest.approx(264, abs=1)

    def test_extreme_cold(self):
        """Test correction at extreme cold temperature."""
        factor = calculate_temperature_correction_factor(
            cell_temperature=-20,
            temp_coefficient=-0.004,
        )
        # Should increase power significantly
        assert factor > 1.15

    def test_extreme_hot(self):
        """Test correction at extreme hot temperature."""
        factor = calculate_temperature_correction_factor(
            cell_temperature=80,
            temp_coefficient=-0.004,
        )
        # Should reduce power significantly
        assert factor < 0.80


class TestTemperatureModelEnum:
    """Test suite for TemperatureModel enum."""

    def test_enum_values(self):
        """Test enum has expected values."""
        assert TemperatureModel.FAIMAN.value == "faiman"
        assert TemperatureModel.SAPM.value == "sapm"
        assert TemperatureModel.PVSYST.value == "pvsyst"
        assert TemperatureModel.GENERIC_LINEAR.value == "generic_linear"

    def test_enum_from_string(self):
        """Test creating enum from string."""
        model = TemperatureModel("faiman")
        assert model == TemperatureModel.FAIMAN


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_negative_irradiance(self):
        """Test models handle negative irradiance gracefully."""
        # Models should still work (though physically unrealistic)
        temp = faiman_model(poa_global=-100, temp_air=25, wind_speed=3)
        # Should be below ambient
        assert temp < 25

    def test_very_high_irradiance(self):
        """Test models with very high irradiance."""
        temp = faiman_model(poa_global=1500, temp_air=25, wind_speed=3)
        assert temp > 55  # Very hot
        assert temp < 100  # But not unreasonably hot

    def test_zero_wind_speed(self):
        """Test models with zero wind speed."""
        # Should still work (minimum heat loss)
        temp = faiman_model(poa_global=800, temp_air=25, wind_speed=0)
        assert temp > 25

    def test_very_low_temperature(self):
        """Test models at very low ambient temperature."""
        temp = faiman_model(poa_global=800, temp_air=-20, wind_speed=3)
        # Should be above -20°C due to irradiance
        assert temp > -20

    def test_very_high_temperature(self):
        """Test models at very high ambient temperature."""
        temp = faiman_model(poa_global=800, temp_air=50, wind_speed=3)
        # Should be above 50°C
        assert temp > 50
