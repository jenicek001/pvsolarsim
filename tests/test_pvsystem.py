"""Tests for PVSystem model."""

import pytest

from pvsolarsim.core.pvsystem import PVSystem


class TestPVSystem:
    """Test suite for PVSystem configuration."""

    def test_pvsystem_valid(self):
        """Test valid PVSystem creation."""
        system = PVSystem(
            panel_area=20.0, panel_efficiency=0.20, tilt=35.0, azimuth=180.0
        )
        assert system.panel_area == 20.0
        assert system.panel_efficiency == 0.20
        assert system.tilt == 35.0
        assert system.azimuth == 180.0
        assert system.temp_coefficient == -0.004  # Default

    def test_pvsystem_custom_temp_coefficient(self):
        """Test PVSystem with custom temperature coefficient."""
        system = PVSystem(
            panel_area=10.0,
            panel_efficiency=0.18,
            tilt=30.0,
            azimuth=180.0,
            temp_coefficient=-0.0045,
        )
        assert system.temp_coefficient == -0.0045

    def test_pvsystem_invalid_panel_area(self):
        """Test invalid panel area raises error."""
        with pytest.raises(ValueError, match="Panel area must be positive"):
            PVSystem(panel_area=0, panel_efficiency=0.20, tilt=35.0, azimuth=180.0)

        with pytest.raises(ValueError, match="Panel area must be positive"):
            PVSystem(panel_area=-10, panel_efficiency=0.20, tilt=35.0, azimuth=180.0)

    def test_pvsystem_invalid_efficiency(self):
        """Test invalid panel efficiency raises error."""
        with pytest.raises(ValueError, match="Panel efficiency must be 0-1"):
            PVSystem(panel_area=20.0, panel_efficiency=0, tilt=35.0, azimuth=180.0)

        with pytest.raises(ValueError, match="Panel efficiency must be 0-1"):
            PVSystem(panel_area=20.0, panel_efficiency=1.5, tilt=35.0, azimuth=180.0)

    def test_pvsystem_invalid_tilt(self):
        """Test invalid tilt raises error."""
        with pytest.raises(ValueError, match="Tilt must be 0-90 degrees"):
            PVSystem(panel_area=20.0, panel_efficiency=0.20, tilt=-10, azimuth=180.0)

        with pytest.raises(ValueError, match="Tilt must be 0-90 degrees"):
            PVSystem(panel_area=20.0, panel_efficiency=0.20, tilt=95, azimuth=180.0)

    def test_pvsystem_invalid_azimuth(self):
        """Test invalid azimuth raises error."""
        with pytest.raises(ValueError, match="Azimuth must be 0-360 degrees"):
            PVSystem(panel_area=20.0, panel_efficiency=0.20, tilt=35.0, azimuth=-10)

        with pytest.raises(ValueError, match="Azimuth must be 0-360 degrees"):
            PVSystem(panel_area=20.0, panel_efficiency=0.20, tilt=35.0, azimuth=370)

    def test_pvsystem_edge_values(self):
        """Test edge case values."""
        # Horizontal panel
        system = PVSystem(panel_area=10.0, panel_efficiency=0.20, tilt=0, azimuth=180.0)
        assert system.tilt == 0

        # Vertical panel
        system = PVSystem(panel_area=10.0, panel_efficiency=0.20, tilt=90, azimuth=180.0)
        assert system.tilt == 90

        # North-facing
        system = PVSystem(panel_area=10.0, panel_efficiency=0.20, tilt=35.0, azimuth=0)
        assert system.azimuth == 0

        # Maximum efficiency (theoretical)
        system = PVSystem(panel_area=10.0, panel_efficiency=1.0, tilt=35.0, azimuth=180.0)
        assert system.panel_efficiency == 1.0
