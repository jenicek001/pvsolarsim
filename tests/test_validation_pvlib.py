"""Validation tests comparing PVSolarSim with pvlib-python.

These tests ensure that our calculations match the industry-standard
pvlib-python library, validating accuracy and correctness.
"""

from datetime import datetime

import numpy as np
import pandas as pd
import pytest
import pytz

# Import pvlib for comparison
try:
    import pvlib
    PVLIB_AVAILABLE = True
except ImportError:
    PVLIB_AVAILABLE = False

from pvsolarsim import Location, PVSystem
from pvsolarsim.atmosphere import calculate_clearsky_irradiance, ClearSkyModel
from pvsolarsim.irradiance import calculate_poa_irradiance
from pvsolarsim.solar import calculate_solar_position


pytestmark = pytest.mark.skipif(not PVLIB_AVAILABLE, reason="pvlib not available")


class TestSolarPositionValidation:
    """Validate solar position calculations against pvlib."""

    @pytest.fixture
    def test_locations(self):
        """Test locations covering different latitudes."""
        return [
            (40.0, -105.0, 1655, "America/Denver"),  # Colorado
            (51.5, -0.1, 10, "Europe/London"),  # London
            (35.7, 139.7, 40, "Asia/Tokyo"),  # Tokyo
            (0.0, 0.0, 0, "UTC"),  # Equator
            (-33.9, 18.4, 20, "Africa/Johannesburg"),  # Cape Town
            (64.8, -147.9, 136, "America/Anchorage"),  # Fairbanks (high latitude)
        ]

    @pytest.fixture
    def test_times(self):
        """Test times covering different seasons and times of day."""
        utc = pytz.UTC
        return [
            utc.localize(datetime(2025, 6, 21, 12, 0, 0)),  # Summer solstice, noon
            utc.localize(datetime(2025, 12, 21, 12, 0, 0)),  # Winter solstice, noon
            utc.localize(datetime(2025, 3, 20, 6, 0, 0)),  # Spring equinox, dawn
            utc.localize(datetime(2025, 9, 23, 18, 0, 0)),  # Fall equinox, dusk
            utc.localize(datetime(2025, 1, 1, 0, 0, 0)),  # New year, midnight
        ]

    def test_solar_position_vs_pvlib_single(self, test_locations, test_times):
        """Test solar position against pvlib for single calculations."""
        for lat, lon, alt, tz in test_locations:
            for timestamp in test_times:
                # Calculate using PVSolarSim
                pvss_pos = calculate_solar_position(timestamp, lat, lon, alt)
                
                # Calculate using pvlib
                pvlib_pos = pvlib.solarposition.get_solarposition(
                    timestamp, lat, lon, altitude=alt, method="nrel_numpy"
                )
                
                # Compare results (allow small differences due to different implementations)
                assert abs(pvss_pos.azimuth - pvlib_pos["azimuth"].iloc[0]) < 0.01, \
                    f"Azimuth mismatch at {lat}, {lon}, {timestamp}"
                assert abs(pvss_pos.zenith - pvlib_pos["zenith"].iloc[0]) < 0.01, \
                    f"Zenith mismatch at {lat}, {lon}, {timestamp}"
                assert abs(pvss_pos.elevation - pvlib_pos["elevation"].iloc[0]) < 0.01, \
                    f"Elevation mismatch at {lat}, {lon}, {timestamp}"

    def test_solar_position_accuracy(self):
        """Test solar position accuracy is within spec (<0.01° error)."""
        # NREL test case from SPA validation data
        timestamp = pytz.UTC.localize(datetime(2003, 10, 17, 12, 30, 30))
        lat, lon, alt = 39.742476, -105.1786, 1830.14
        
        location = Location(latitude=lat, longitude=lon, altitude=alt)
        pos = calculate_solar_position(timestamp, location.latitude, location.longitude, location.altitude)
        
        # Expected values from NREL SPA (via pvlib)
        pvlib_pos = pvlib.solarposition.get_solarposition(
            timestamp, lat, lon, altitude=alt, method="nrel_numpy"
        )
        
        # Should be within 0.01° as spec'd
        azimuth_error = abs(pos.azimuth - pvlib_pos["azimuth"].iloc[0])
        elevation_error = abs(pos.elevation - pvlib_pos["elevation"].iloc[0])
        
        assert azimuth_error < 0.01, f"Azimuth error {azimuth_error}° exceeds spec"
        assert elevation_error < 0.01, f"Elevation error {elevation_error}° exceeds spec"


class TestClearSkyValidation:
    """Validate clear-sky irradiance calculations against pvlib."""

    def test_ineichen_vs_pvlib(self):
        """Test Ineichen model against pvlib."""
        # Test parameters
        times = pd.date_range("2025-06-21 06:00", "2025-06-21 18:00", freq="h", tz="UTC")
        lat, lon, alt = 40.0, -105.0, 1655
        
        location = Location(latitude=lat, longitude=lon, altitude=alt)
        
        for timestamp in times:
            # Calculate solar position
            solar_pos = calculate_solar_position(timestamp, location.latitude, location.longitude, location.altitude)
            
            if solar_pos.elevation > 0:  # Daytime only
                # Calculate using PVSolarSim
                pvss_irr = calculate_clearsky_irradiance(
                    solar_zenith=solar_pos.zenith,
                    solar_azimuth=solar_pos.azimuth,
                    altitude=alt,
                    model=ClearSkyModel.INEICHEN,
                    linke_turbidity=3.0,
                )
                
                # Calculate using pvlib
                pvlib_irr = pvlib.clearsky.ineichen(
                    apparent_zenith=solar_pos.zenith,
                    airmass_absolute=pvlib.atmosphere.get_absolute_airmass(
                        pvlib.atmosphere.get_relative_airmass(solar_pos.zenith),
                        pressure=pvlib.atmosphere.alt2pres(alt)
                    ),
                    linke_turbidity=3.0,
                    altitude=alt,
                )
                
                # Compare (allow small numerical differences)
                ghi_error_pct = abs(pvss_irr.ghi - pvlib_irr["ghi"].iloc[0]) / pvlib_irr["ghi"].iloc[0] * 100
                dni_error_pct = abs(pvss_irr.dni - pvlib_irr["dni"].iloc[0]) / pvlib_irr["dni"].iloc[0] * 100
                
                # Should be within 2% as per spec
                assert ghi_error_pct < 2.0, f"GHI error {ghi_error_pct:.2f}% exceeds 2% at {timestamp}"
                assert dni_error_pct < 2.0, f"DNI error {dni_error_pct:.2f}% exceeds 2% at {timestamp}"

    def test_simplified_solis_vs_pvlib(self):
        """Test Simplified Solis model against pvlib."""
        # Test at noon on summer solstice
        timestamp = pytz.UTC.localize(datetime(2025, 6, 21, 12, 0, 0))
        lat, lon, alt = 40.0, -105.0, 1655
        
        location = Location(latitude=lat, longitude=lon, altitude=alt)
        solar_pos = calculate_solar_position(timestamp, location.latitude, location.longitude, location.altitude)
        
        # Calculate using PVSolarSim
        pvss_irr = calculate_clearsky_irradiance(
            solar_zenith=solar_pos.zenith,
            solar_azimuth=solar_pos.azimuth,
            altitude=alt,
            model=ClearSkyModel.SIMPLIFIED_SOLIS,
            aod700=0.1,
            precipitable_water=1.5,
        )
        
        # Calculate using pvlib
        pvlib_irr = pvlib.clearsky.simplified_solis(
            apparent_elevation=solar_pos.elevation,
            aod700=0.1,
            precipitable_water=1.5,
            pressure=pvlib.atmosphere.alt2pres(alt),
        )
        
        # Should match closely since we're delegating to pvlib
        assert abs(pvss_irr.ghi - pvlib_irr["ghi"]) < 1.0  # Within 1 W/m²
        assert abs(pvss_irr.dni - pvlib_irr["dni"]) < 1.0
        assert abs(pvss_irr.dhi - pvlib_irr["dhi"]) < 1.0


class TestPOAIrradianceValidation:
    """Validate POA irradiance calculations against pvlib."""

    def test_poa_perez_vs_pvlib(self):
        """Test POA calculation with Perez model against pvlib."""
        # Test parameters
        timestamp = pytz.UTC.localize(datetime(2025, 6, 21, 12, 0, 0))
        lat, lon, alt = 40.0, -105.0, 1655
        surface_tilt = 35.0
        surface_azimuth = 180.0  # South-facing
        
        location = Location(latitude=lat, longitude=lon, altitude=alt)
        solar_pos = calculate_solar_position(timestamp, location.latitude, location.longitude, location.altitude)
        
        # Get clear-sky irradiance
        clear_sky = calculate_clearsky_irradiance(
            solar_zenith=solar_pos.zenith,
            solar_azimuth=solar_pos.azimuth,
            altitude=alt,
            model=ClearSkyModel.INEICHEN,
        )
        
        # Calculate POA using PVSolarSim
        pvss_poa = calculate_poa_irradiance(
            surface_tilt=surface_tilt,
            surface_azimuth=surface_azimuth,
            solar_zenith=solar_pos.zenith,
            solar_azimuth=solar_pos.azimuth,
            dni=clear_sky.dni,
            dhi=clear_sky.dhi,
            ghi=clear_sky.ghi,
            diffuse_model="perez",
            albedo=0.2,
        )
        
        # Calculate POA using pvlib
        pvlib_poa = pvlib.irradiance.get_total_irradiance(
            surface_tilt=surface_tilt,
            surface_azimuth=surface_azimuth,
            solar_zenith=solar_pos.zenith,
            solar_azimuth=solar_pos.azimuth,
            dni=clear_sky.dni,
            dhi=clear_sky.dhi,
            ghi=clear_sky.ghi,
            model="perez",
            albedo=0.2,
        )
        
        # Compare
        poa_error_pct = abs(pvss_poa.poa_global - pvlib_poa["poa_global"]) / pvlib_poa["poa_global"] * 100
        assert poa_error_pct < 1.0, f"POA global error {poa_error_pct:.2f}% exceeds 1%"

    def test_poa_isotropic_vs_pvlib(self):
        """Test POA calculation with isotropic model against pvlib."""
        timestamp = pytz.UTC.localize(datetime(2025, 6, 21, 15, 0, 0))
        lat, lon = 40.0, -105.0
        surface_tilt = 30.0
        surface_azimuth = 180.0
        
        location = Location(latitude=lat, longitude=lon)
        solar_pos = calculate_solar_position(timestamp, location.latitude, location.longitude, location.altitude)
        
        # Sample irradiance
        dni, dhi, ghi = 800.0, 100.0, 850.0
        
        # Calculate POA using PVSolarSim
        pvss_poa = calculate_poa_irradiance(
            surface_tilt=surface_tilt,
            surface_azimuth=surface_azimuth,
            solar_zenith=solar_pos.zenith,
            solar_azimuth=solar_pos.azimuth,
            dni=dni,
            dhi=dhi,
            ghi=ghi,
            diffuse_model="isotropic",
        )
        
        # Calculate POA using pvlib
        pvlib_poa = pvlib.irradiance.get_total_irradiance(
            surface_tilt=surface_tilt,
            surface_azimuth=surface_azimuth,
            solar_zenith=solar_pos.zenith,
            solar_azimuth=solar_pos.azimuth,
            dni=dni,
            dhi=dhi,
            ghi=ghi,
            model="isotropic",
        )
        
        # Should match closely
        assert abs(pvss_poa.poa_global - pvlib_poa["poa_global"]) < 1.0


class TestTemperatureModelsValidation:
    """Validate temperature models against pvlib."""

    def test_faiman_vs_pvlib(self):
        """Test Faiman temperature model against pvlib."""
        from pvsolarsim.temperature import calculate_cell_temperature
        
        poa_global = 800.0
        temp_air = 25.0
        wind_speed = 3.0
        
        # Calculate using PVSolarSim
        pvss_temp = calculate_cell_temperature(
            poa_global=poa_global,
            temp_air=temp_air,
            wind_speed=wind_speed,
            model="faiman",
        )
        
        # Calculate using pvlib (Faiman model)
        pvlib_temp = pvlib.temperature.faiman(
            poa_global=poa_global,
            temp_air=temp_air,
            wind_speed=wind_speed,
        )
        
        # Should match closely
        assert abs(pvss_temp - pvlib_temp) < 0.1, f"Temperature difference: {abs(pvss_temp - pvlib_temp):.2f}°C"

    def test_sapm_vs_pvlib(self):
        """Test SAPM temperature model against pvlib."""
        from pvsolarsim.temperature import calculate_cell_temperature
        
        poa_global = 1000.0
        temp_air = 30.0
        wind_speed = 2.0
        
        # Calculate using PVSolarSim
        pvss_temp = calculate_cell_temperature(
            poa_global=poa_global,
            temp_air=temp_air,
            wind_speed=wind_speed,
            model="sapm",
        )
        
        # Calculate using pvlib (SAPM model with default module params)
        # Note: pvlib SAPM uses different parameters, so we expect similar but not exact match
        pvlib_temp = pvlib.temperature.sapm_cell(
            poa_global=poa_global,
            temp_air=temp_air,
            wind_speed=wind_speed,
            a=-3.47,  # Default open rack glass/cell/polymer sheet
            b=-0.0594,
            deltaT=3,
        )
        
        # Should be reasonably close (within a few degrees)
        assert abs(pvss_temp - pvlib_temp) < 5.0, f"Temperature difference: {abs(pvss_temp - pvlib_temp):.2f}°C"


class TestAccuracyMetrics:
    """Calculate and document accuracy metrics (RMSE, MAE, MAPE)."""

    def test_solar_position_accuracy_metrics(self):
        """Calculate accuracy metrics for solar position over a full day."""
        # Full day simulation
        times = pd.date_range("2025-06-21", periods=24, freq="h", tz="UTC")
        lat, lon, alt = 40.0, -105.0, 1655
        
        location = Location(latitude=lat, longitude=lon, altitude=alt)
        
        azimuth_errors = []
        elevation_errors = []
        
        for timestamp in times:
            pvss_pos = calculate_solar_position(timestamp, location.latitude, location.longitude, location.altitude)
            pvlib_pos = pvlib.solarposition.get_solarposition(
                timestamp, lat, lon, altitude=alt, method="nrel_numpy"
            )
            
            azimuth_errors.append(abs(pvss_pos.azimuth - pvlib_pos["azimuth"].iloc[0]))
            elevation_errors.append(abs(pvss_pos.elevation - pvlib_pos["elevation"].iloc[0]))
        
        # Calculate metrics
        azimuth_rmse = np.sqrt(np.mean(np.array(azimuth_errors)**2))
        elevation_rmse = np.sqrt(np.mean(np.array(elevation_errors)**2))
        
        azimuth_mae = np.mean(azimuth_errors)
        elevation_mae = np.mean(elevation_errors)
        
        # Document metrics
        print("\n=== Solar Position Accuracy Metrics ===")
        print(f"Azimuth RMSE: {azimuth_rmse:.4f}°")
        print(f"Azimuth MAE: {azimuth_mae:.4f}°")
        print(f"Elevation RMSE: {elevation_rmse:.4f}°")
        print(f"Elevation MAE: {elevation_mae:.4f}°")
        
        # Assert within spec
        assert azimuth_rmse < 0.01, f"Azimuth RMSE {azimuth_rmse}° exceeds 0.01°"
        assert elevation_rmse < 0.01, f"Elevation RMSE {elevation_rmse}° exceeds 0.01°"

    def test_clearsky_accuracy_metrics(self):
        """Calculate accuracy metrics for clear-sky irradiance over a day."""
        times = pd.date_range("2025-06-21 06:00", "2025-06-21 18:00", freq="h", tz="UTC")
        lat, lon, alt = 40.0, -105.0, 1655
        
        location = Location(latitude=lat, longitude=lon, altitude=alt)
        
        ghi_errors = []
        dni_errors = []
        
        for timestamp in times:
            solar_pos = calculate_solar_position(timestamp, location.latitude, location.longitude, location.altitude)
            
            if solar_pos.elevation > 0:
                pvss_irr = calculate_clearsky_irradiance(
                    solar_zenith=solar_pos.zenith,
                    solar_azimuth=solar_pos.azimuth,
                    altitude=alt,
                    model=ClearSkyModel.INEICHEN,
                )
                
                pvlib_irr = pvlib.clearsky.ineichen(
                    apparent_zenith=solar_pos.zenith,
                    airmass_absolute=pvlib.atmosphere.get_absolute_airmass(
                        pvlib.atmosphere.get_relative_airmass(solar_pos.zenith),
                        pressure=pvlib.atmosphere.alt2pres(alt)
                    ),
                    linke_turbidity=3.0,
                    altitude=alt,
                )
                
                ghi_errors.append(abs(pvss_irr.ghi - pvlib_irr["ghi"].iloc[0]) / pvlib_irr["ghi"].iloc[0] * 100)
                dni_errors.append(abs(pvss_irr.dni - pvlib_irr["dni"].iloc[0]) / pvlib_irr["dni"].iloc[0] * 100)
        
        # Calculate MAPE (Mean Absolute Percentage Error)
        ghi_mape = np.mean(ghi_errors)
        dni_mape = np.mean(dni_errors)
        
        print("\n=== Clear-Sky Irradiance Accuracy Metrics ===")
        print(f"GHI MAPE: {ghi_mape:.2f}%")
        print(f"DNI MAPE: {dni_mape:.2f}%")
        
        # Assert within spec (< 2%)
        assert ghi_mape < 2.0, f"GHI MAPE {ghi_mape:.2f}% exceeds 2%"
        assert dni_mape < 2.0, f"DNI MAPE {dni_mape:.2f}% exceeds 2%"
