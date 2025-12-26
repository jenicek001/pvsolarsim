"""
Solar position calculations using the Solar Position Algorithm (SPA).

This module provides functions to calculate the position of the sun
for any location and time on Earth. The implementation uses pvlib-python's
SPA implementation for high accuracy (<0.01° error).

References
----------
.. [1] Reda, I., & Andreas, A. (2004). Solar position algorithm for solar
       radiation applications. Solar Energy, 76(5), 577-589.
"""

from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import pvlib  # type: ignore[import-untyped]

__all__ = ["SolarPosition", "calculate_solar_position"]


@dataclass
class SolarPosition:
    """
    Solar position data.

    Attributes
    ----------
    azimuth : float
        Solar azimuth angle in degrees (0° = North, 90° = East, 180° = South)
    zenith : float
        Solar zenith angle in degrees (0° = overhead, 90° = horizon)
    elevation : float
        Solar elevation angle in degrees (90° - zenith)
    """

    azimuth: float
    zenith: float
    elevation: float


def calculate_solar_position(
    timestamp: datetime,
    latitude: float,
    longitude: float,
    altitude: float = 0,
) -> SolarPosition:
    """
    Calculate solar position for a single timestamp.

    Uses the Solar Position Algorithm (SPA) for high accuracy (<0.01° error).
    This function delegates to pvlib.solarposition.get_solarposition for
    validated, accurate calculations.

    Parameters
    ----------
    timestamp : datetime
        Time of calculation (must be timezone-aware)
    latitude : float
        Latitude in decimal degrees (-90 to 90, North positive)
    longitude : float
        Longitude in decimal degrees (-180 to 180, East positive)
    altitude : float, optional
        Altitude above sea level in meters (default: 0)

    Returns
    -------
    SolarPosition
        Dataclass containing azimuth, zenith, elevation angles

    Raises
    ------
    ValueError
        If latitude or longitude out of valid range, or timestamp not timezone-aware

    Examples
    --------
    >>> from datetime import datetime
    >>> import pytz
    >>> timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)
    >>> pos = calculate_solar_position(timestamp, 49.8, 15.5, 300)
    >>> print(f"Azimuth: {pos.azimuth:.2f}°")
    Azimuth: 183.45°

    References
    ----------
    .. [1] Reda, I., & Andreas, A. (2004). Solar position algorithm for solar
           radiation applications. Solar Energy, 76(5), 577-589.
    """
    # Validate inputs
    if not -90 <= latitude <= 90:
        raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
    if not -180 <= longitude <= 180:
        raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")
    if timestamp.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")

    # Create time index for pvlib
    times = pd.DatetimeIndex([timestamp])

    # Calculate solar position using pvlib
    solar_pos = pvlib.solarposition.get_solarposition(
        times, latitude, longitude, altitude=altitude, method="nrel_numpy"
    )

    # Extract values
    azimuth = float(solar_pos["azimuth"].iloc[0])
    zenith = float(solar_pos["apparent_zenith"].iloc[0])
    elevation = float(solar_pos["apparent_elevation"].iloc[0])

    return SolarPosition(azimuth=azimuth, zenith=zenith, elevation=elevation)
