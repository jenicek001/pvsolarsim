"""Core data models for PVSolarSim."""

from dataclasses import dataclass


@dataclass
class Location:
    """Geographic location for PV simulation.

    Attributes:
        latitude: Latitude in decimal degrees (-90 to 90)
        longitude: Longitude in decimal degrees (-180 to 180)
        altitude: Altitude above sea level in meters (default: 0)
        timezone: IANA timezone string (e.g., "Europe/Prague")
    """

    latitude: float
    longitude: float
    altitude: float = 0.0
    timezone: str = "UTC"

    def __post_init__(self) -> None:
        """Validate location parameters."""
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {self.longitude}")
        if self.altitude < -500:  # Dead Sea is ~-430m
            raise ValueError(f"Altitude seems unrealistic: {self.altitude}m")
