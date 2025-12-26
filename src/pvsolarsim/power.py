"""Power calculation for PV systems.

This module provides functions to calculate instantaneous and time-series power output
from PV systems by integrating solar position, atmospheric modeling, POA irradiance,
and temperature effects.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

import numpy as np

from pvsolarsim.atmosphere import (
    ClearSkyModel,
    IrradianceComponents,
    apply_cloud_cover,
    calculate_clearsky_irradiance,
)
from pvsolarsim.core.location import Location
from pvsolarsim.core.pvsystem import PVSystem
from pvsolarsim.irradiance import calculate_poa_irradiance
from pvsolarsim.solar import calculate_solar_position
from pvsolarsim.temperature import (
    calculate_cell_temperature,
    calculate_temperature_correction_factor,
)


@dataclass
class PowerResult:
    """Result from power calculation.

    Attributes:
        power_w: DC power output in Watts
        power_ac_w: AC power output in Watts (if inverter efficiency provided)
        poa_irradiance: Plane-of-array global irradiance (W/m²)
        poa_direct: POA direct irradiance (W/m²)
        poa_diffuse: POA diffuse irradiance (W/m²)
        cell_temperature: Cell temperature (°C)
        ghi: Global horizontal irradiance (W/m²)
        dni: Direct normal irradiance (W/m²)
        dhi: Diffuse horizontal irradiance (W/m²)
        solar_elevation: Solar elevation angle (degrees)
        solar_azimuth: Solar azimuth angle (degrees)
        temperature_factor: Temperature correction factor (0-1+)
    """

    power_w: Union[float, np.ndarray]
    poa_irradiance: Union[float, np.ndarray]
    poa_direct: Union[float, np.ndarray]
    poa_diffuse: Union[float, np.ndarray]
    cell_temperature: Union[float, np.ndarray]
    ghi: Union[float, np.ndarray]
    dni: Union[float, np.ndarray]
    dhi: Union[float, np.ndarray]
    solar_elevation: Union[float, np.ndarray]
    solar_azimuth: Union[float, np.ndarray]
    temperature_factor: Union[float, np.ndarray]
    power_ac_w: Optional[Union[float, np.ndarray]] = None


def calculate_power(
    location: Location,
    system: PVSystem,
    timestamp: datetime,
    ambient_temp: float = 25.0,
    wind_speed: float = 1.0,
    cloud_cover: float = 0,
    ghi: Optional[float] = None,
    dni: Optional[float] = None,
    dhi: Optional[float] = None,
    clearsky_model: Union[str, ClearSkyModel] = ClearSkyModel.INEICHEN,
    diffuse_model: str = "perez",
    temperature_model: str = "faiman",
    albedo: float = 0.2,
    soiling_factor: float = 1.0,
    degradation_factor: float = 1.0,
    inverter_efficiency: Optional[float] = None,
) -> PowerResult:
    """Calculate instantaneous PV power output.

    This function integrates all components of PV modeling:
    1. Solar position calculation
    2. Clear-sky or user-provided irradiance
    3. Cloud cover adjustment
    4. Plane-of-array irradiance calculation
    5. Cell temperature modeling
    6. Power calculation with temperature correction
    7. Optional AC power with inverter efficiency

    Args:
        location: Geographic location
        system: PV system configuration
        timestamp: Time for calculation (timezone-aware)
        ambient_temp: Ambient air temperature (°C), default 25
        wind_speed: Wind speed (m/s), default 1.0
        cloud_cover: Cloud cover (0-100% or 0-1), default 0
        ghi: Global horizontal irradiance (W/m²), optional
        dni: Direct normal irradiance (W/m²), optional
        dhi: Diffuse horizontal irradiance (W/m²), optional
        clearsky_model: Clear-sky model if GHI/DNI/DHI not provided
        diffuse_model: Diffuse transposition model ('isotropic', 'perez', 'haydavies')
        temperature_model: Cell temperature model ('faiman', 'sapm', 'pvsyst', 'generic_linear')
        albedo: Ground reflectance (0-1), default 0.2
        soiling_factor: Soiling losses (0-1, 1=clean), default 1.0
        degradation_factor: Degradation factor (0-1), default 1.0
        inverter_efficiency: Inverter efficiency (0-1), optional

    Returns:
        PowerResult with power and intermediate values

    Raises:
        ValueError: If timestamp is not timezone-aware or if invalid parameters

    Examples:
        >>> from pvsolarsim import Location, PVSystem, calculate_power
        >>> from datetime import datetime
        >>> import pytz
        >>>
        >>> location = Location(latitude=49.8, longitude=15.5, altitude=300)
        >>> system = PVSystem(panel_area=20.0, panel_efficiency=0.20, tilt=35, azimuth=180)
        >>> timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)
        >>>
        >>> # Calculate with clear sky
        >>> result = calculate_power(location, system, timestamp, ambient_temp=25, wind_speed=3)
        >>> print(f"Power: {result.power_w:.2f} W")
        >>>
        >>> # Calculate with cloud cover
        >>> result = calculate_power(
        ...     location, system, timestamp,
        ...     ambient_temp=25, wind_speed=3, cloud_cover=50
        ... )
        >>>
        >>> # Calculate with provided irradiance data
        >>> result = calculate_power(
        ...     location, system, timestamp,
        ...     ghi=800, dni=700, dhi=150,
        ...     ambient_temp=25, wind_speed=3
        ... )
    """
    # Validate timestamp
    if timestamp.tzinfo is None:
        raise ValueError("Timestamp must be timezone-aware")

    # Step 1: Calculate solar position
    solar_pos = calculate_solar_position(
        timestamp=timestamp,
        latitude=location.latitude,
        longitude=location.longitude,
        altitude=location.altitude,
    )

    # If sun is below horizon, return zero power
    if solar_pos.elevation <= 0:
        return PowerResult(
            power_w=0.0,
            poa_irradiance=0.0,
            poa_direct=0.0,
            poa_diffuse=0.0,
            cell_temperature=ambient_temp,
            ghi=0.0,
            dni=0.0,
            dhi=0.0,
            solar_elevation=solar_pos.elevation,
            solar_azimuth=solar_pos.azimuth,
            temperature_factor=1.0,
            power_ac_w=0.0 if inverter_efficiency is not None else None,
        )

    # Step 2: Get irradiance components
    if ghi is not None and dni is not None and dhi is not None:
        # User-provided irradiance
        irradiance = IrradianceComponents(ghi=ghi, dni=dni, dhi=dhi)
    else:
        # Calculate clear-sky irradiance
        irradiance = calculate_clearsky_irradiance(
            apparent_elevation=solar_pos.elevation,
            latitude=location.latitude,
            longitude=location.longitude,
            altitude=location.altitude,
            model=clearsky_model,
        )

        # Apply cloud cover if specified
        if cloud_cover > 0:
            cloud_adjusted = apply_cloud_cover(
                ghi=irradiance.ghi,
                dni=irradiance.dni,
                dhi=irradiance.dhi,
                cloud_cover=cloud_cover,
                solar_elevation=solar_pos.elevation,
            )
            irradiance = IrradianceComponents(
                ghi=cloud_adjusted.ghi,
                dni=cloud_adjusted.dni,
                dhi=cloud_adjusted.dhi,
            )

    # Step 3: Calculate plane-of-array irradiance
    poa = calculate_poa_irradiance(
        surface_tilt=system.tilt,
        surface_azimuth=system.azimuth,
        solar_zenith=solar_pos.zenith,
        solar_azimuth=solar_pos.azimuth,
        dni=irradiance.dni,
        ghi=irradiance.ghi,
        dhi=irradiance.dhi,
        diffuse_model=diffuse_model,
        albedo=albedo,
    )

    # Step 4: Calculate cell temperature
    cell_temp = calculate_cell_temperature(
        poa_global=poa.poa_global,
        temp_air=ambient_temp,
        wind_speed=wind_speed,
        model=temperature_model,
    )

    # Step 5: Calculate temperature correction factor
    temp_factor = calculate_temperature_correction_factor(
        cell_temperature=cell_temp,
        temp_coefficient=system.temp_coefficient,
    )

    # Step 6: Calculate DC power
    # P_DC = Area * Efficiency * POA * temp_factor * soiling * degradation
    power_dc = (
        system.panel_area
        * system.panel_efficiency
        * poa.poa_global
        * temp_factor
        * soiling_factor
        * degradation_factor
    )

    # Step 7: Calculate AC power if inverter efficiency provided
    power_ac = None
    if inverter_efficiency is not None:
        power_ac = power_dc * inverter_efficiency

    return PowerResult(
        power_w=power_dc,
        poa_irradiance=poa.poa_global,
        poa_direct=poa.poa_direct,
        poa_diffuse=poa.poa_diffuse,
        cell_temperature=cell_temp,
        ghi=irradiance.ghi,
        dni=irradiance.dni,
        dhi=irradiance.dhi,
        solar_elevation=solar_pos.elevation,
        solar_azimuth=solar_pos.azimuth,
        temperature_factor=temp_factor,
        power_ac_w=power_ac,
    )
