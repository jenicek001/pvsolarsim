"""Atmospheric modeling for solar irradiance calculations."""

from pvsolarsim.atmosphere.clearsky import (
    ClearSkyModel,
    IrradianceComponents,
    calculate_clearsky_irradiance,
)
from pvsolarsim.atmosphere.cloudcover import (
    CloudAdjustedIrradiance,
    CloudCoverModel,
    apply_cloud_cover,
    calculate_cloud_attenuation,
)

__all__ = [
    "ClearSkyModel",
    "IrradianceComponents",
    "calculate_clearsky_irradiance",
    "CloudCoverModel",
    "CloudAdjustedIrradiance",
    "apply_cloud_cover",
    "calculate_cloud_attenuation",
]
