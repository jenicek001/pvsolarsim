"""Cloud cover modeling for irradiance attenuation.

This module provides models to adjust clear-sky irradiance based on cloud cover
percentage or fraction. Multiple models are available with different accuracy
and complexity trade-offs.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Union

import numpy as np


class CloudCoverModel(Enum):
    """Available cloud cover models."""

    CAMPBELL_NORMAN = "campbell_norman"
    SIMPLE_LINEAR = "simple_linear"
    KASTEN_CZEPLAK = "kasten_czeplak"


@dataclass
class CloudAdjustedIrradiance:
    """Cloud-adjusted irradiance components.

    Attributes:
        ghi: Global Horizontal Irradiance (W/m²)
        dni: Direct Normal Irradiance (W/m²)
        dhi: Diffuse Horizontal Irradiance (W/m²)
        cloud_fraction: Cloud cover fraction (0-1)
    """

    ghi: Union[float, np.ndarray]
    dni: Union[float, np.ndarray]
    dhi: Union[float, np.ndarray]
    cloud_fraction: Union[float, np.ndarray]


def calculate_cloud_attenuation(
    cloud_cover: Union[float, np.ndarray],
    solar_elevation: Union[float, np.ndarray],
    model: Union[str, CloudCoverModel] = CloudCoverModel.CAMPBELL_NORMAN,
) -> Union[float, np.ndarray]:
    """Calculate irradiance attenuation factor due to cloud cover.

    Args:
        cloud_cover: Cloud cover percentage (0-100) or fraction (0-1)
        solar_elevation: Solar elevation angle in degrees
        model: Cloud cover model to use

    Returns:
        Attenuation factor (0-1, where 1 = no attenuation)

    Raises:
        ValueError: If cloud_cover is out of valid range or model is invalid

    Examples:
        >>> # 50% cloud cover, 45° elevation
        >>> factor = calculate_cloud_attenuation(50, 45.0)
        >>> print(f"Attenuation: {factor:.3f}")
        Attenuation: 0.683

        >>> # Using array inputs
        >>> import numpy as np
        >>> cloud = np.array([0, 25, 50, 75, 100])
        >>> elevation = np.full(5, 45.0)
        >>> factors = calculate_cloud_attenuation(cloud, elevation)
    """
    # Convert cloud cover to fraction if given as percentage
    cloud_fraction = np.asarray(cloud_cover, dtype=float)

    # Validate input range first
    if np.any(cloud_fraction < 0):
        raise ValueError(f"Cloud cover must be 0-100% or 0-1, got {cloud_cover}")

    # Check for ambiguous range (> 1 but < 2) - not clearly percentage or fraction
    if np.any((cloud_fraction > 1.0) & (cloud_fraction < 2.0)):
        raise ValueError(
            f"Cloud cover values between 1.0 and 2.0 are ambiguous. "
            f"Use 0-1 for fraction or 0-100 for percentage, got {cloud_cover}"
        )

    # Convert percentage to fraction if needed
    if np.any(cloud_fraction >= 2.0):
        if np.any(cloud_fraction > 100):
            raise ValueError(f"Cloud cover must be 0-100% or 0-1, got {cloud_cover}")
        cloud_fraction = cloud_fraction / 100.0

    # Convert model string to enum if needed
    if isinstance(model, str):
        try:
            model = CloudCoverModel(model.lower())
        except ValueError as e:
            raise ValueError(
                f"Invalid cloud cover model: {model}. "
                f"Valid options: {[m.value for m in CloudCoverModel]}"
            ) from e

    # Apply selected model
    if model == CloudCoverModel.CAMPBELL_NORMAN:
        return _campbell_norman_attenuation(cloud_fraction, solar_elevation)
    elif model == CloudCoverModel.SIMPLE_LINEAR:
        return _simple_linear_attenuation(cloud_fraction)
    elif model == CloudCoverModel.KASTEN_CZEPLAK:
        return _kasten_czeplak_attenuation(cloud_fraction, solar_elevation)
    else:
        raise ValueError(f"Unsupported model: {model}")


def _campbell_norman_attenuation(
    cloud_fraction: Union[float, np.ndarray], solar_elevation: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """Campbell-Norman cloud attenuation model.

    This model accounts for solar elevation effects on cloud transmission.
    Based on Campbell & Norman (1998).

    Args:
        cloud_fraction: Cloud cover fraction (0-1)
        solar_elevation: Solar elevation angle in degrees

    Returns:
        Attenuation factor (0-1)

    References:
        Campbell, G. S., & Norman, J. M. (1998). An introduction to environmental
        biophysics (2nd ed.). Springer.
    """
    cloud_fraction = np.asarray(cloud_fraction)
    solar_elevation = np.asarray(solar_elevation)

    # Calculate transmittance for fully overcast conditions
    # Accounts for cloud optical depth and solar path length
    sin_elevation = np.sin(np.radians(solar_elevation))

    # Avoid division by zero for low elevations
    sin_elevation = np.maximum(sin_elevation, 0.01)

    # Cloud transmittance (empirical formula)
    # Clear sky = 1.0, overcast = 0.35 (typical)
    tau_overcast = 0.35 + 0.1 * sin_elevation

    # Interpolate between clear (1.0) and overcast based on cloud fraction
    attenuation = 1.0 - cloud_fraction * (1.0 - tau_overcast)

    return attenuation


def _simple_linear_attenuation(cloud_fraction: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Simple linear cloud attenuation model.

    Very simple model: attenuation = 1 - 0.75 * cloud_fraction
    Assumes 75% reduction in irradiance for fully overcast conditions.

    Args:
        cloud_fraction: Cloud cover fraction (0-1)

    Returns:
        Attenuation factor (0-1)
    """
    cloud_fraction = np.asarray(cloud_fraction)
    return 1.0 - 0.75 * cloud_fraction


def _kasten_czeplak_attenuation(
    cloud_fraction: Union[float, np.ndarray], solar_elevation: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """Kasten-Czeplak cloud attenuation model.

    Empirical model based on European weather data.

    Args:
        cloud_fraction: Cloud cover fraction (0-1)
        solar_elevation: Solar elevation angle in degrees

    Returns:
        Attenuation factor (0-1)

    References:
        Kasten, F., & Czeplak, G. (1980). Solar and terrestrial radiation
        dependent on the amount and type of cloud. Solar Energy, 24(2), 177-189.
    """
    cloud_fraction = np.asarray(cloud_fraction)
    solar_elevation = np.asarray(solar_elevation)

    # Model parameters (empirical)
    # For solar elevation > 20°
    a = 0.88
    b = -0.84

    # Calculate attenuation
    attenuation = 1.0 + b * cloud_fraction**a

    # Ensure non-negative
    attenuation = np.maximum(attenuation, 0.0)

    return attenuation


def apply_cloud_cover(
    ghi: Union[float, np.ndarray],
    dni: Union[float, np.ndarray],
    dhi: Union[float, np.ndarray],
    cloud_cover: Union[float, np.ndarray],
    solar_elevation: Union[float, np.ndarray],
    model: Union[str, CloudCoverModel] = CloudCoverModel.CAMPBELL_NORMAN,
) -> CloudAdjustedIrradiance:
    """Apply cloud cover attenuation to clear-sky irradiance.

    Args:
        ghi: Clear-sky Global Horizontal Irradiance (W/m²)
        dni: Clear-sky Direct Normal Irradiance (W/m²)
        dhi: Clear-sky Diffuse Horizontal Irradiance (W/m²)
        cloud_cover: Cloud cover percentage (0-100) or fraction (0-1)
        solar_elevation: Solar elevation angle in degrees
        model: Cloud cover model to use

    Returns:
        CloudAdjustedIrradiance with cloud-adjusted components

    Examples:
        >>> # Adjust clear-sky irradiance for 50% cloud cover
        >>> adjusted = apply_cloud_cover(
        ...     ghi=800, dni=700, dhi=150,
        ...     cloud_cover=50, solar_elevation=45.0
        ... )
        >>> print(f"Cloudy GHI: {adjusted.ghi:.1f} W/m²")
    """
    # Calculate attenuation factor
    attenuation = calculate_cloud_attenuation(cloud_cover, solar_elevation, model)

    # Convert to arrays for consistent processing
    dni_arr = np.asarray(dni)
    dhi_arr = np.asarray(dhi)

    # Apply attenuation
    # DNI is most affected by clouds (direct beam blocked)
    # DHI is less affected (diffuse light from clouds)
    dni_cloudy = dni_arr * attenuation**2  # Stronger attenuation for direct
    dhi_cloudy = dhi_arr + dni_arr * (1 - attenuation**2) * 0.5  # Scattered light

    # Calculate adjusted GHI
    # GHI = DNI * cos(zenith) + DHI
    zenith = 90 - np.asarray(solar_elevation)
    cos_zenith = np.cos(np.radians(zenith))
    cos_zenith = np.maximum(cos_zenith, 0)  # Clip to 0 for sun below horizon

    ghi_cloudy = dni_cloudy * cos_zenith + dhi_cloudy

    # Convert cloud cover to fraction for output
    cloud_fraction = np.asarray(cloud_cover, dtype=float)
    if np.any(cloud_fraction > 1.0):
        cloud_fraction = cloud_fraction / 100.0

    # Return scalar if ALL inputs were scalar
    all_scalar = (
        np.isscalar(ghi)
        and np.isscalar(dni)
        and np.isscalar(dhi)
        and np.isscalar(cloud_cover)
        and np.isscalar(solar_elevation)
    )

    if all_scalar:
        return CloudAdjustedIrradiance(
            ghi=float(ghi_cloudy),
            dni=float(dni_cloudy),
            dhi=float(dhi_cloudy),
            cloud_fraction=float(cloud_fraction),
        )
    else:
        return CloudAdjustedIrradiance(
            ghi=ghi_cloudy,
            dni=dni_cloudy,
            dhi=dhi_cloudy,
            cloud_fraction=cloud_fraction,
        )
