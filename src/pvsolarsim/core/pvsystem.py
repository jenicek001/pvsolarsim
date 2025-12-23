"""PV system configuration."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PVSystem:
    """PV system configuration.

    Attributes:
        panel_area: Total panel area in square meters
        panel_efficiency: Panel efficiency (0-1, e.g., 0.20 for 20%)
        tilt: Panel tilt angle from horizontal in degrees (0-90)
        azimuth: Panel azimuth angle in degrees (0=North, 90=East, 180=South, 270=West)
        temp_coefficient: Temperature coefficient of power (%/°C), typically negative (e.g., -0.004)
    """

    panel_area: float
    panel_efficiency: float
    tilt: float
    azimuth: float
    temp_coefficient: float = -0.004

    def __post_init__(self):
        """Validate system parameters."""
        if self.panel_area <= 0:
            raise ValueError(f"Panel area must be positive, got {self.panel_area}")
        if not 0 < self.panel_efficiency <= 1:
            raise ValueError(f"Panel efficiency must be 0-1, got {self.panel_efficiency}")
        if not 0 <= self.tilt <= 90:
            raise ValueError(f"Tilt must be 0-90 degrees, got {self.tilt}")
        if not 0 <= self.azimuth <= 360:
            raise ValueError(f"Azimuth must be 0-360 degrees, got {self.azimuth}")
