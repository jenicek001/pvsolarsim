"""
Clear-sky irradiance models.

This module provides multiple clear-sky irradiance models to calculate
theoretical solar irradiance under cloudless conditions.

Models implemented:
- Ineichen: Industry standard, uses Linke turbidity
- Simplified Solis: Good balance of accuracy and speed

References
----------
.. [1] Ineichen, P., & Perez, R. (2002). A new airmass independent formulation for
       the Linke turbidity coefficient. Solar Energy, 73(3), 151-157.
.. [2] Ineichen, P. (2008). A broadband simplified version of the Solis clear sky
       model. Solar Energy, 82(8), 758-762.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Union

import numpy as np
import pvlib  # type: ignore[import-untyped]

__all__ = ["IrradianceComponents", "ClearSkyModel", "calculate_clearsky_irradiance"]


@dataclass
class IrradianceComponents:
    """
    Irradiance components.

    Attributes
    ----------
    ghi : float or ndarray
        Global Horizontal Irradiance in W/m²
    dni : float or ndarray
        Direct Normal Irradiance in W/m²
    dhi : float or ndarray
        Diffuse Horizontal Irradiance in W/m²
    """

    ghi: Union[float, np.ndarray]
    dni: Union[float, np.ndarray]
    dhi: Union[float, np.ndarray]


class ClearSkyModel(str, Enum):
    """Available clear-sky models."""

    INEICHEN = "ineichen"
    SIMPLIFIED_SOLIS = "simplified_solis"


def calculate_clearsky_irradiance(
    apparent_elevation: float,
    latitude: float,
    longitude: float,
    altitude: float = 0,
    model: Union[str, ClearSkyModel] = ClearSkyModel.INEICHEN,
    linke_turbidity: float = 3.0,
) -> IrradianceComponents:
    """
    Calculate clear-sky irradiance using specified model.

    This function uses pvlib's clear-sky models for validated, accurate calculations.

    Parameters
    ----------
    apparent_elevation : float
        Apparent solar elevation angle in degrees
    latitude : float
        Latitude in decimal degrees
    longitude : float
        Longitude in decimal degrees
    altitude : float, optional
        Altitude above sea level in meters (default: 0)
    model : str or ClearSkyModel, optional
        Clear-sky model to use (default: "ineichen")
    linke_turbidity : float, optional
        Linke turbidity factor (default: 3.0, typical clear sky)
        Range: 1.0 (extremely clear) to 7.0+ (very turbid/polluted)

    Returns
    -------
    IrradianceComponents
        Dataclass containing GHI, DNI, DHI values

    Raises
    ------
    ValueError
        If elevation is negative (sun below horizon) or model is invalid

    Examples
    --------
    >>> irradiance = calculate_clearsky_irradiance(
    ...     apparent_elevation=45.0,
    ...     latitude=49.8,
    ...     longitude=15.5,
    ...     altitude=300,
    ...     model="ineichen",
    ...     linke_turbidity=3.0
    ... )
    >>> print(f"GHI: {irradiance.ghi:.2f} W/m²")
    GHI: 850.00 W/m²

    Notes
    -----
    For sun below horizon (elevation < 0), returns zero irradiance.

    References
    ----------
    .. [1] Ineichen, P., & Perez, R. (2002). A new airmass independent formulation
           for the Linke turbidity coefficient. Solar Energy, 73(3), 151-157.
    """
    # Validate model
    if isinstance(model, str):
        try:
            model = ClearSkyModel(model.lower())
        except ValueError as e:
            raise ValueError(
                f"Invalid clear-sky model: {model}. "
                f"Available models: {[m.value for m in ClearSkyModel]}"
            ) from e

    # Handle sun below horizon
    if apparent_elevation < 0:
        return IrradianceComponents(ghi=0.0, dni=0.0, dhi=0.0)

    # Calculate using pvlib
    # Note: pvlib requires zenith angle
    apparent_zenith = 90 - apparent_elevation

    # For Ineichen model, use pvlib.clearsky.ineichen
    if model == ClearSkyModel.INEICHEN:
        result = pvlib.clearsky.ineichen(
            apparent_zenith=apparent_zenith,
            airmass_absolute=pvlib.atmosphere.get_absolute_airmass(
                pvlib.atmosphere.get_relative_airmass(apparent_zenith)
            ),
            linke_turbidity=linke_turbidity,
            altitude=altitude,
        )
    elif model == ClearSkyModel.SIMPLIFIED_SOLIS:
        result = pvlib.clearsky.simplified_solis(
            apparent_elevation=apparent_elevation,
            aod700=0.1,  # Default aerosol optical depth at 700nm
            precipitable_water=1.5,  # Default precipitable water in cm
            pressure=pvlib.atmosphere.alt2pres(altitude),
        )
    else:
        raise ValueError(f"Model {model} not implemented")

    return IrradianceComponents(
        ghi=float(result["ghi"]), dni=float(result["dni"]), dhi=float(result["dhi"])
    )
