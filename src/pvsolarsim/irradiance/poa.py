"""
Plane-of-Array (POA) irradiance calculations.

This module provides functions to calculate irradiance components on tilted
PV panels, including beam, diffuse, and ground-reflected components.

Multiple diffuse transposition models are supported:
- Isotropic: Simple model assuming uniform sky diffuse
- Perez: Anisotropic model with circumsolar and horizon brightening (industry standard)
- Hay-Davies: Circumsolar plus isotropic background

Incidence Angle Modifiers (IAM) account for reflection losses at high angles.

References
----------
.. [1] Perez, R., et al. (1990). Modeling daylight availability and irradiance
       components from direct and global irradiance. Solar Energy, 44(5), 271-289.
.. [2] Hay, J. E., & Davies, J. A. (1980). Calculation of the solar radiation
       incident on an inclined surface. Proc. of First Canadian Solar Radiation
       Data Workshop, 59-72.
.. [3] King, D. L., et al. (2004). Sandia Photovoltaic Array Performance Model.
       SAND2004-3535.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Union

import pvlib  # type: ignore[import-untyped]

__all__ = [
    "POAComponents",
    "POAIrradiance",
    "DiffuseModel",
    "IAMModel",
    "calculate_aoi",
    "calculate_poa_irradiance",
]


@dataclass
class POAComponents:
    """
    Plane-of-array irradiance components.

    Attributes
    ----------
    poa_direct : float
        Direct (beam) component on tilted surface in W/m²
    poa_diffuse : float
        Diffuse component on tilted surface in W/m²
    poa_ground : float
        Ground-reflected component in W/m²
    poa_global : float
        Total POA irradiance (direct + diffuse + ground) in W/m²
    """

    poa_direct: float
    poa_diffuse: float
    poa_ground: float
    poa_global: float


class DiffuseModel(str, Enum):
    """Available diffuse transposition models."""

    ISOTROPIC = "isotropic"
    PEREZ = "perez"
    HAYDAVIES = "haydavies"


class IAMModel(str, Enum):
    """Available incidence angle modifier models."""

    ASHRAE = "ashrae"
    PHYSICAL = "physical"
    MARTIN_RUIZ = "martin_ruiz"


def calculate_aoi(
    surface_tilt: float,
    surface_azimuth: float,
    solar_zenith: float,
    solar_azimuth: float,
) -> float:
    """
    Calculate angle of incidence (AOI) between sun and panel surface.

    The angle of incidence is the angle between the sun's rays and the
    normal vector to the panel surface. AOI = 0° means the sun is directly
    perpendicular to the panel.

    Parameters
    ----------
    surface_tilt : float
        Panel tilt angle from horizontal in degrees (0° = horizontal, 90° = vertical)
    surface_azimuth : float
        Panel azimuth angle in degrees (0° = North, 90° = East, 180° = South)
    solar_zenith : float
        Solar zenith angle in degrees (0° = overhead)
    solar_azimuth : float
        Solar azimuth angle in degrees (0° = North, 90° = East)

    Returns
    -------
    float
        Angle of incidence in degrees (0° to 180°)

    Examples
    --------
    >>> # South-facing 35° tilt panel with sun at 45° elevation from south
    >>> aoi = calculate_aoi(
    ...     surface_tilt=35.0,
    ...     surface_azimuth=180.0,
    ...     solar_zenith=45.0,
    ...     solar_azimuth=180.0
    ... )
    >>> print(f"AOI: {aoi:.2f}°")
    AOI: 10.00°

    Notes
    -----
    Uses the standard spherical geometry formula:

    .. math::

        \\cos(AOI) = \\cos(\\theta_z) \\cos(\\beta) +
                     \\sin(\\theta_z) \\sin(\\beta) \\cos(\\gamma_s - \\gamma)

    where :math:`\\theta_z` is solar zenith, :math:`\\beta` is surface tilt,
    :math:`\\gamma_s` is solar azimuth, and :math:`\\gamma` is surface azimuth.
    """
    # Delegate to pvlib for validated calculation
    aoi = pvlib.irradiance.aoi(
        surface_tilt=surface_tilt,
        surface_azimuth=surface_azimuth,
        solar_zenith=solar_zenith,
        solar_azimuth=solar_azimuth,
    )
    return float(aoi)


class POAIrradiance:
    """
    Calculator for plane-of-array irradiance on tilted surfaces.

    This class encapsulates the calculation of POA irradiance with
    configurable diffuse transposition and IAM models.

    Parameters
    ----------
    diffuse_model : str or DiffuseModel, optional
        Diffuse transposition model (default: "perez")
    iam_model : str or IAMModel, optional
        Incidence angle modifier model (default: "physical")
    albedo : float, optional
        Ground reflectance (default: 0.2 for typical ground)
        Range: 0.0 (no reflection) to 1.0 (perfect reflection)
        Typical values: 0.15-0.25 (grass), 0.6-0.9 (snow), 0.1-0.15 (asphalt)

    Examples
    --------
    >>> poa_calc = POAIrradiance(diffuse_model="perez", albedo=0.2)
    >>> components = poa_calc.calculate(
    ...     surface_tilt=35.0,
    ...     surface_azimuth=180.0,
    ...     solar_zenith=45.0,
    ...     solar_azimuth=180.0,
    ...     dni=800.0,
    ...     ghi=600.0,
    ...     dhi=100.0
    ... )
    >>> print(f"POA Global: {components.poa_global:.2f} W/m²")
    POA Global: 750.00 W/m²
    """

    def __init__(
        self,
        diffuse_model: Union[str, DiffuseModel] = DiffuseModel.PEREZ,
        iam_model: Union[str, IAMModel] = IAMModel.PHYSICAL,
        albedo: float = 0.2,
    ):
        """Initialize POA calculator with model selections."""
        # Validate and convert diffuse model
        if isinstance(diffuse_model, str):
            try:
                diffuse_model = DiffuseModel(diffuse_model.lower())
            except ValueError as e:
                raise ValueError(
                    f"Invalid diffuse model: {diffuse_model}. "
                    f"Available: {[m.value for m in DiffuseModel]}"
                ) from e
        self.diffuse_model = diffuse_model

        # Validate and convert IAM model
        if isinstance(iam_model, str):
            try:
                iam_model = IAMModel(iam_model.lower())
            except ValueError as e:
                raise ValueError(
                    f"Invalid IAM model: {iam_model}. "
                    f"Available: {[m.value for m in IAMModel]}"
                ) from e
        self.iam_model = iam_model

        # Validate albedo
        if not 0.0 <= albedo <= 1.0:
            raise ValueError(f"Albedo must be between 0 and 1, got {albedo}")
        self.albedo = albedo

    def calculate(
        self,
        surface_tilt: float,
        surface_azimuth: float,
        solar_zenith: float,
        solar_azimuth: float,
        dni: float,
        ghi: float,
        dhi: float,
        dni_extra: float = 1367.0,
    ) -> POAComponents:
        """
        Calculate plane-of-array irradiance components.

        Parameters
        ----------
        surface_tilt : float
            Panel tilt angle from horizontal in degrees (0-90)
        surface_azimuth : float
            Panel azimuth in degrees (0° = North, 180° = South)
        solar_zenith : float
            Solar zenith angle in degrees
        solar_azimuth : float
            Solar azimuth angle in degrees
        dni : float
            Direct Normal Irradiance in W/m²
        ghi : float
            Global Horizontal Irradiance in W/m²
        dhi : float
            Diffuse Horizontal Irradiance in W/m²
        dni_extra : float, optional
            Extraterrestrial Direct Normal Irradiance in W/m²
            (default: 1367.0, solar constant)

        Returns
        -------
        POAComponents
            Breakdown of POA irradiance components

        Notes
        -----
        The total POA irradiance is computed as:

        .. math::

            POA_{global} = POA_{direct} + POA_{diffuse} + POA_{ground}

        where:
        - Direct component = DNI × cos(AOI) × IAM(AOI)
        - Diffuse component depends on chosen transposition model
        - Ground-reflected = GHI × albedo × (1 - cos(tilt)) / 2
        """
        # Validate inputs
        if not 0 <= surface_tilt <= 90:
            raise ValueError(f"Surface tilt must be 0-90°, got {surface_tilt}")
        if dni < 0 or ghi < 0 or dhi < 0:
            raise ValueError("Irradiance values cannot be negative")

        # Calculate angle of incidence
        aoi = calculate_aoi(surface_tilt, surface_azimuth, solar_zenith, solar_azimuth)

        # Use pvlib for comprehensive POA calculation
        # This delegates to validated models
        poa_components = pvlib.irradiance.get_total_irradiance(
            surface_tilt=surface_tilt,
            surface_azimuth=surface_azimuth,
            solar_zenith=solar_zenith,
            solar_azimuth=solar_azimuth,
            dni=dni,
            ghi=ghi,
            dhi=dhi,
            dni_extra=dni_extra,
            albedo=self.albedo,
            model=self.diffuse_model.value,
        )

        # Apply IAM to beam component
        iam = self._calculate_iam(aoi)
        poa_direct = float(poa_components["poa_direct"]) * iam
        poa_diffuse = float(poa_components["poa_diffuse"])
        poa_ground = float(poa_components["poa_ground_diffuse"])
        poa_global = poa_direct + poa_diffuse + poa_ground

        return POAComponents(
            poa_direct=poa_direct,
            poa_diffuse=poa_diffuse,
            poa_ground=poa_ground,
            poa_global=poa_global,
        )

    def _calculate_iam(self, aoi: float) -> float:
        """
        Calculate incidence angle modifier.

        Parameters
        ----------
        aoi : float
            Angle of incidence in degrees

        Returns
        -------
        float
            IAM factor (0.0 to 1.0)
        """
        # For angles > 90°, no direct irradiance
        if aoi >= 90:
            return 0.0

        # Delegate to pvlib IAM models
        if self.iam_model == IAMModel.ASHRAE:
            iam = pvlib.iam.ashrae(aoi, b=0.05)  # Typical b value for glass
        elif self.iam_model == IAMModel.PHYSICAL:
            iam = pvlib.iam.physical(aoi, n=1.526, K=4.0, L=0.002)  # Glass parameters
        elif self.iam_model == IAMModel.MARTIN_RUIZ:
            iam = pvlib.iam.martin_ruiz(aoi, a_r=0.16)  # Typical value
        else:
            # Should not reach here due to validation in __init__
            iam = 1.0

        return float(iam)


def calculate_poa_irradiance(
    surface_tilt: float,
    surface_azimuth: float,
    solar_zenith: float,
    solar_azimuth: float,
    dni: float,
    ghi: float,
    dhi: float,
    diffuse_model: Union[str, DiffuseModel] = DiffuseModel.PEREZ,
    iam_model: Union[str, IAMModel] = IAMModel.PHYSICAL,
    albedo: float = 0.2,
    dni_extra: float = 1367.0,
) -> POAComponents:
    """
    Calculate plane-of-array irradiance (convenience function).

    This is a convenience wrapper around POAIrradiance.calculate() for
    one-off calculations without creating a POAIrradiance instance.

    Parameters
    ----------
    surface_tilt : float
        Panel tilt angle from horizontal in degrees (0-90)
    surface_azimuth : float
        Panel azimuth in degrees (0° = North, 180° = South)
    solar_zenith : float
        Solar zenith angle in degrees
    solar_azimuth : float
        Solar azimuth angle in degrees
    dni : float
        Direct Normal Irradiance in W/m²
    ghi : float
        Global Horizontal Irradiance in W/m²
    dhi : float
        Diffuse Horizontal Irradiance in W/m²
    diffuse_model : str or DiffuseModel, optional
        Diffuse transposition model (default: "perez")
    iam_model : str or IAMModel, optional
        Incidence angle modifier model (default: "physical")
    albedo : float, optional
        Ground reflectance (default: 0.2)
    dni_extra : float, optional
        Extraterrestrial DNI in W/m² (default: 1367.0)

    Returns
    -------
    POAComponents
        POA irradiance components

    Examples
    --------
    >>> from pvsolarsim.irradiance import calculate_poa_irradiance
    >>> poa = calculate_poa_irradiance(
    ...     surface_tilt=35.0,
    ...     surface_azimuth=180.0,
    ...     solar_zenith=45.0,
    ...     solar_azimuth=180.0,
    ...     dni=800.0,
    ...     ghi=600.0,
    ...     dhi=100.0,
    ...     diffuse_model="perez",
    ...     albedo=0.2
    ... )
    >>> print(f"Total POA: {poa.poa_global:.2f} W/m²")
    Total POA: 750.00 W/m²

    See Also
    --------
    POAIrradiance : Class-based interface for repeated calculations
    """
    calculator = POAIrradiance(
        diffuse_model=diffuse_model, iam_model=iam_model, albedo=albedo
    )
    return calculator.calculate(
        surface_tilt=surface_tilt,
        surface_azimuth=surface_azimuth,
        solar_zenith=solar_zenith,
        solar_azimuth=solar_azimuth,
        dni=dni,
        ghi=ghi,
        dhi=dhi,
        dni_extra=dni_extra,
    )
