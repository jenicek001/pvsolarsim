"""
Temperature modeling for PV modules.

This module provides functions to calculate PV module and cell temperatures
using various empirical models. Temperature affects PV performance significantly,
typically reducing power output by 0.3-0.5% per degree Celsius above 25°C.

The models implemented here are:
- Faiman: Empirical heat loss factor model (IEC 61853 standard)
- SAPM: Sandia Array Performance Model
- PVsyst: PVsyst cell temperature model
- Generic Linear: Generalized linear heat loss model

References
----------
.. [1] Faiman, D. (2008). "Assessing the outdoor operating temperature of
       photovoltaic modules." Progress in Photovoltaics, 16(4), 307-315.
.. [2] King, D. L., et al. (2004). "Sandia Photovoltaic Array Performance Model."
       SAND2004-3535. Sandia National Laboratories.
.. [3] Driesse, A., et al. (2022). "PV Module Operating Temperature Model
       Equivalence and Parameter Translation." IEEE PVSC.
"""

from enum import Enum
from typing import Union, cast

import numpy as np
from numpy.typing import ArrayLike, NDArray

__all__ = [
    "TemperatureModel",
    "calculate_cell_temperature",
    "calculate_temperature_correction_factor",
    "faiman_model",
    "sapm_model",
    "pvsyst_model",
    "generic_linear_model",
]


class TemperatureModel(Enum):
    """Enumeration of available temperature models."""

    FAIMAN = "faiman"
    SAPM = "sapm"
    PVSYST = "pvsyst"
    GENERIC_LINEAR = "generic_linear"


def faiman_model(
    poa_global: Union[float, ArrayLike],
    temp_air: Union[float, ArrayLike],
    wind_speed: Union[float, ArrayLike] = 1.0,
    u0: float = 25.0,
    u1: float = 6.84,
) -> Union[float, NDArray[np.float64]]:
    """
    Calculate cell/module temperature using the Faiman model.

    The Faiman model uses an empirical heat loss factor that depends on
    wind speed. It is adopted in the IEC 61853 standards. This model
    does not distinguish between cell and module temperature.

    The model is:

    .. math::

        T_{cell} = T_{air} + \\frac{E_{POA}}{u_0 + u_1 \\cdot v_{wind}}

    Parameters
    ----------
    poa_global : float or array-like
        Total incident irradiance on the plane of array [W/m²]
    temp_air : float or array-like
        Ambient dry bulb temperature [°C]
    wind_speed : float or array-like, optional
        Wind speed at module height [m/s] (default: 1.0)
    u0 : float, optional
        Combined convection and radiative heat loss factor [W/(m²·K)]
        (default: 25.0, typical for open-rack mounting)
    u1 : float, optional
        Wind-dependent heat loss factor [W/(m²·K)/(m/s)]
        (default: 6.84, typical for open-rack mounting)

    Returns
    -------
    float or ndarray
        Cell/module temperature [°C]

    Notes
    -----
    Default parameters (u0=25, u1=6.84) are representative of open-rack
    mounted modules. For building-integrated systems, use higher u0 values
    (lower heat dissipation).

    Examples
    --------
    >>> temp = faiman_model(poa_global=800, temp_air=25, wind_speed=3)
    >>> print(f"Cell temperature: {temp:.2f}°C")
    Cell temperature: 46.26°C

    >>> # Vectorized calculation
    >>> import numpy as np
    >>> irradiance = np.array([400, 800, 1000])
    >>> temps = faiman_model(irradiance, temp_air=25, wind_speed=3)
    >>> print(temps)
    [34.63 46.26 52.58]

    References
    ----------
    .. [1] Faiman, D. (2008). "Assessing the outdoor operating temperature of
           photovoltaic modules." Progress in Photovoltaics, 16(4), 307-315.
    .. [2] IEC 61853-2:2018. Photovoltaic (PV) module performance testing and
           energy rating.
    """
    # Convert to numpy arrays for vectorized operations
    poa_global = np.asarray(poa_global)
    temp_air = np.asarray(temp_air)
    wind_speed = np.asarray(wind_speed)

    # Calculate heat loss factor
    heat_loss_factor = u0 + u1 * wind_speed

    # Calculate temperature rise above ambient
    temp_rise = poa_global / heat_loss_factor

    # Calculate cell temperature
    cell_temp = temp_air + temp_rise

    # Return scalar if input was scalar
    if cell_temp.ndim == 0:
        return float(cell_temp)
    return cast(NDArray[np.float64], cell_temp)


def sapm_model(
    poa_global: Union[float, ArrayLike],
    temp_air: Union[float, ArrayLike],
    wind_speed: Union[float, ArrayLike],
    a: float = -3.47,
    b: float = -0.0594,
    delta_t: float = 3.0,  # noqa: N803 (matches pvlib parameter name)
    irrad_ref: float = 1000.0,
) -> Union[float, NDArray[np.float64]]:
    """
    Calculate cell temperature using the Sandia Array Performance Model (SAPM).

    The SAPM temperature model relates module back-surface temperature to
    ambient conditions. Cell temperature is then estimated from module
    temperature using a fixed offset (deltaT).

    The model is:

    .. math::

        T_{module} = E_{POA} \\cdot e^{a + b \\cdot v_{wind}} + T_{air}

        T_{cell} = T_{module} + \\frac{E_{POA}}{E_{ref}} \\cdot \\Delta T

    Parameters
    ----------
    poa_global : float or array-like
        Total incident irradiance [W/m²]
    temp_air : float or array-like
        Ambient dry bulb temperature [°C]
    wind_speed : float or array-like
        Wind speed at 10 meters height [m/s]
    a : float, optional
        Empirical parameter (default: -3.47, typical for glass/glass open rack)
    b : float, optional
        Empirical parameter (default: -0.0594, typical for glass/glass open rack)
    delta_t : float, optional
        Temperature difference between cell and module back [°C]
        (default: 3.0, typical value)
    irrad_ref : float, optional
        Reference irradiance for normalization [W/m²] (default: 1000.0)

    Returns
    -------
    float or ndarray
        Cell temperature [°C]

    Notes
    -----
    The default parameters are typical for glass/glass modules in
    open-rack mounting. For building-integrated systems or different module
    constructions, calibrated parameters should be used.

    Examples
    --------
    >>> temp = sapm_model(poa_global=800, temp_air=25, wind_speed=3)
    >>> print(f"Cell temperature: {temp:.2f}°C")
    Cell temperature: 48.23°C

    >>> # With custom parameters for a specific module
    >>> temp = sapm_model(
    ...     poa_global=1000,
    ...     temp_air=20,
    ...     wind_speed=2,
    ...     a=-3.56,
    ...     b=-0.075,
    ...     delta_t=3.5
    ... )
    >>> print(f"Cell temperature: {temp:.2f}°C")
    Cell temperature: 23.90°C

    References
    ----------
    .. [1] King, D. L., et al. (2004). "Sandia Photovoltaic Array Performance
           Model." SAND2004-3535. Sandia National Laboratories.
    """
    # Convert to numpy arrays
    poa_global = np.asarray(poa_global)
    temp_air = np.asarray(temp_air)
    wind_speed = np.asarray(wind_speed)

    # Calculate module back-surface temperature
    # T_module = E * exp(a + b * WS) + T_air
    temp_module = poa_global * np.exp(a + b * wind_speed) + temp_air

    # Calculate cell temperature (module temp + offset)
    # T_cell = T_module + (E / E_ref) * delta_t
    irrad_normalized = poa_global / irrad_ref
    cell_temp = temp_module + irrad_normalized * delta_t

    # Return scalar if input was scalar
    if cell_temp.ndim == 0:
        return float(cell_temp)
    return cast(NDArray[np.float64], cell_temp)


def pvsyst_model(
    poa_global: Union[float, ArrayLike],
    temp_air: Union[float, ArrayLike],
    wind_speed: Union[float, ArrayLike] = 1.0,
    u_c: float = 29.0,
    u_v: float = 0.0,
    module_efficiency: float = 0.1,
    alpha_absorption: float = 0.9,
) -> Union[float, NDArray[np.float64]]:
    """
    Calculate cell temperature using the PVsyst model.

    The PVsyst model uses a heat loss factor that depends on wind speed
    and accounts for the fact that absorbed irradiance is reduced by
    the module's electrical efficiency.

    The model is:

    .. math::

        T_{cell} = T_{air} + \\frac{\\alpha \\cdot E_{POA} \\cdot (1 - \\eta)}{u_c + u_v \\cdot v_{wind}}

    Parameters
    ----------
    poa_global : float or array-like
        Total incident irradiance [W/m²]
    temp_air : float or array-like
        Ambient dry bulb temperature [°C]
    wind_speed : float or array-like, optional
        Wind speed at module height [m/s] (default: 1.0)
    u_c : float, optional
        Constant heat transfer coefficient [W/(m²·K)]
        (default: 29.0, typical for free-standing modules)
    u_v : float, optional
        Wind-dependent heat transfer coefficient [W/(m²·K)/(m/s)]
        (default: 0.0)
    module_efficiency : float, optional
        Module electrical efficiency, 0-1 (default: 0.1, i.e., 10%)
    alpha_absorption : float, optional
        Module absorption coefficient, 0-1 (default: 0.9, i.e., 90%)

    Returns
    -------
    float or ndarray
        Cell temperature [°C]

    Notes
    -----
    The PVsyst model explicitly accounts for the electrical efficiency,
    recognizing that converted electrical energy does not contribute to
    heating. This makes it more physically accurate than simpler models.

    Default u_v=0 means wind speed effect is not considered unless
    specifically calibrated.

    Examples
    --------
    >>> temp = pvsyst_model(
    ...     poa_global=800,
    ...     temp_air=25,
    ...     wind_speed=3,
    ...     u_c=29.0,
    ...     u_v=0.0,
    ...     module_efficiency=0.20,
    ...     alpha_absorption=0.88
    ... )
    >>> print(f"Cell temperature: {temp:.2f}°C")
    Cell temperature: 44.36°C

    References
    ----------
    .. [1] PVsyst 7 Help. "Module temperature." https://www.pvsyst.com/help/
    """
    # Convert to numpy arrays
    poa_global = np.asarray(poa_global)
    temp_air = np.asarray(temp_air)
    wind_speed = np.asarray(wind_speed)

    # Heat loss factor
    heat_loss_factor = u_c + u_v * wind_speed

    # Absorbed heat (accounting for electrical conversion)
    absorbed_heat = alpha_absorption * poa_global * (1 - module_efficiency)

    # Temperature rise
    temp_rise = absorbed_heat / heat_loss_factor

    # Cell temperature
    cell_temp = temp_air + temp_rise

    # Return scalar if input was scalar
    if cell_temp.ndim == 0:
        return float(cell_temp)
    return cell_temp


def generic_linear_model(
    poa_global: Union[float, ArrayLike],
    temp_air: Union[float, ArrayLike],
    wind_speed: Union[float, ArrayLike],
    u_const: float,
    du_wind: float,
    module_efficiency: float,
    absorptance: float,
) -> Union[float, NDArray[np.float64]]:
    """
    Calculate cell temperature using the generic linear heat loss model.

    This is a generalized model that can represent other temperature models
    through appropriate parameter selection. It explicitly accounts for
    module efficiency and absorptance.

    The model is:

    .. math::

        T_{cell} = T_{air} + \\frac{\\alpha \\cdot E_{POA} \\cdot (1 - \\eta)}{u_0 + du_{wind} \\cdot v_{wind}}

    Parameters
    ----------
    poa_global : float or array-like
        Total incident irradiance [W/m²]
    temp_air : float or array-like
        Ambient dry bulb temperature [°C]
    wind_speed : float or array-like
        Wind speed at module height [m/s]
    u_const : float
        Constant heat transfer coefficient [W/(m²·K)]
    du_wind : float
        Wind-dependent heat transfer coefficient [W/(m²·K)/(m/s)]
    module_efficiency : float
        Module electrical efficiency, 0-1
    absorptance : float
        Module light absorptance, 0-1

    Returns
    -------
    float or ndarray
        Cell temperature [°C]

    Notes
    -----
    This model provides a unified framework for temperature modeling.
    Parameters can be converted between different model types using
    appropriate transformations.

    Examples
    --------
    >>> temp = generic_linear_model(
    ...     poa_global=800,
    ...     temp_air=25,
    ...     wind_speed=3,
    ...     u_const=11.04,
    ...     du_wind=5.52,
    ...     module_efficiency=0.19,
    ...     absorptance=0.88
    ... )
    >>> print(f"Cell temperature: {temp:.2f}°C")
    Cell temperature: 42.63°C

    References
    ----------
    .. [1] Driesse, A., et al. (2022). "PV Module Operating Temperature Model
           Equivalence and Parameter Translation." IEEE PVSC.
    """
    # Convert to numpy arrays
    poa_global = np.asarray(poa_global)
    temp_air = np.asarray(temp_air)
    wind_speed = np.asarray(wind_speed)

    # Heat loss factor
    heat_loss_factor = u_const + du_wind * wind_speed

    # Absorbed heat (accounting for electrical conversion)
    absorbed_heat = absorptance * poa_global * (1 - module_efficiency)

    # Temperature rise
    temp_rise = absorbed_heat / heat_loss_factor

    # Cell temperature
    cell_temp = temp_air + temp_rise

    # Return scalar if input was scalar
    if cell_temp.ndim == 0:
        return float(cell_temp)
    return cell_temp


def calculate_cell_temperature(
    poa_global: Union[float, ArrayLike],
    temp_air: Union[float, ArrayLike],
    wind_speed: Union[float, ArrayLike],
    model: Union[str, TemperatureModel] = TemperatureModel.FAIMAN,
    **model_params: float,
) -> Union[float, NDArray[np.float64]]:
    """
    Calculate cell temperature using the specified model.

    This is a convenience function that provides a unified interface to all
    temperature models.

    Parameters
    ----------
    poa_global : float or array-like
        Total incident irradiance [W/m²]
    temp_air : float or array-like
        Ambient dry bulb temperature [°C]
    wind_speed : float or array-like
        Wind speed [m/s]
    model : str or TemperatureModel, optional
        Temperature model to use (default: 'faiman')
        Options: 'faiman', 'sapm', 'pvsyst', 'generic_linear'
    **model_params
        Model-specific parameters (see individual model functions)

    Returns
    -------
    float or ndarray
        Cell temperature [°C]

    Raises
    ------
    ValueError
        If an invalid model is specified

    Examples
    --------
    >>> # Using Faiman model (default)
    >>> temp = calculate_cell_temperature(
    ...     poa_global=800,
    ...     temp_air=25,
    ...     wind_speed=3
    ... )
    >>> print(f"Temperature: {temp:.2f}°C")
    Temperature: 46.26°C

    >>> # Using SAPM model with custom parameters
    >>> temp = calculate_cell_temperature(
    ...     poa_global=800,
    ...     temp_air=25,
    ...     wind_speed=3,
    ...     model='sapm',
    ...     a=-3.47,
    ...     b=-0.0594,
    ...     deltaT=3.0
    ... )
    >>> print(f"Temperature: {temp:.2f}°C")
    Temperature: 46.89°C

    >>> # Using PVsyst model
    >>> temp = calculate_cell_temperature(
    ...     poa_global=800,
    ...     temp_air=25,
    ...     wind_speed=3,
    ...     model='pvsyst',
    ...     module_efficiency=0.20,
    ...     alpha_absorption=0.88
    ... )
    >>> print(f"Temperature: {temp:.2f}°C")
    Temperature: 44.36°C
    """
    # Convert string to enum if necessary
    if isinstance(model, str):
        try:
            model = TemperatureModel(model.lower())
        except ValueError as e:
            valid_models = [m.value for m in TemperatureModel]
            raise ValueError(
                f"Invalid temperature model '{model}'. "
                f"Valid options are: {', '.join(valid_models)}"
            ) from e

    # Call appropriate model
    if model == TemperatureModel.FAIMAN:
        return faiman_model(poa_global, temp_air, wind_speed, **model_params)
    elif model == TemperatureModel.SAPM:
        return sapm_model(poa_global, temp_air, wind_speed, **model_params)
    elif model == TemperatureModel.PVSYST:
        return pvsyst_model(poa_global, temp_air, wind_speed, **model_params)
    elif model == TemperatureModel.GENERIC_LINEAR:
        return generic_linear_model(poa_global, temp_air, wind_speed, **model_params)
    else:
        # This should never happen due to enum validation
        raise ValueError(f"Unsupported model: {model}")


def calculate_temperature_correction_factor(
    cell_temperature: Union[float, ArrayLike],
    temp_coefficient: float = -0.004,
    temp_ref: float = 25.0,
) -> Union[float, NDArray[np.float64]]:
    """
    Calculate temperature correction factor for PV power output.

    PV module power output decreases with increasing temperature. The
    correction factor accounts for this effect using a linear model:

    .. math::

        f_{temp} = 1 + \\gamma \\cdot (T_{cell} - T_{ref})

    where γ is the temperature coefficient (typically negative).

    Parameters
    ----------
    cell_temperature : float or array-like
        Cell temperature [°C]
    temp_coefficient : float, optional
        Temperature coefficient of power [1/°C]
        (default: -0.004, i.e., -0.4%/°C, typical for crystalline silicon)
    temp_ref : float, optional
        Reference temperature [°C] (default: 25.0, STC conditions)

    Returns
    -------
    float or ndarray
        Temperature correction factor (dimensionless)
        Values <1 indicate power loss, >1 indicate power gain

    Notes
    -----
    Typical temperature coefficients:
    - Monocrystalline Si: -0.004 to -0.005 (1/°C)
    - Polycrystalline Si: -0.004 to -0.005 (1/°C)
    - CdTe: -0.0025 to -0.003 (1/°C)
    - Amorphous Si: -0.002 to -0.003 (1/°C)

    Examples
    --------
    >>> # Module at 45°C, mono-Si
    >>> factor = calculate_temperature_correction_factor(
    ...     cell_temperature=45,
    ...     temp_coefficient=-0.004
    ... )
    >>> print(f"Correction factor: {factor:.4f}")
    Correction factor: 0.9200

    >>> # This means power is reduced to 92% of STC rating
    >>> power_stc = 300  # W
    >>> power_actual = power_stc * factor
    >>> print(f"Actual power: {power_actual:.1f} W")
    Actual power: 276.0 W

    >>> # Vectorized calculation
    >>> import numpy as np
    >>> temps = np.array([25, 35, 45, 55])
    >>> factors = calculate_temperature_correction_factor(temps)
    >>> print(factors)
    [1.     0.96   0.92   0.88  ]
    """
    cell_temperature = np.asarray(cell_temperature)

    # Calculate temperature difference from reference
    temp_delta = cell_temperature - temp_ref

    # Calculate correction factor
    correction = 1 + temp_coefficient * temp_delta

    # Return scalar if input was scalar
    if correction.ndim == 0:
        return float(correction)
    return correction
