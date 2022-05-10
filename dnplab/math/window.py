import numpy as np


def _handle_array(x):
    """Handle array or integer input argument for window functions

    Args:
        x (array_like, int): array or integer

    Returns:
        int: length of array or integer input
    """
    if type(x) == int:
        N = x
    else:
        N = len(x)

    return N


def exponential(x, lw):
    """Calculate exponential window function

    .. math::
        f(x) =  e^{-2t * lw}

    Args:
        x (array_like): Vector of points
        lw (int or float): linewidth

    Returns:
        array: exponential window function
    """
    return np.exp(-np.pi * (x - x[0]) * lw)


def gaussian(x, lw):
    r"""Calculate gaussian window function

    .. math::
        \mathrm{gaussian} = e^{(\sigma * x^{2})}

    Args:
        x (array_like): vector of points
        lw (float): Standard deviation of gaussian window

    Returns:
        array: gaussian window function
    """
    sigma = lw * (
        2.0 * np.sqrt(2.0 * np.log(2.0))

    )  # convert FWHM to standard deviation
#    sigma = 1. / sigma
    return np.exp(-1 * (x**2.0) * (sigma**2.0)/1.5)


def hann(x):
    r"""Calculate hann window function

    .. math::
        \mathrm{han} = 0.5 + 0.5\cos(\pi * n / (N-1))

    Args:
        x (array_like): vector of points
        N(int): number of points to return in window function

    Returns:
        ndarray: hann window function
    """
    N = _handle_array(x)

    return 0.5 + 0.5 * np.cos(1.0 * np.pi * np.arange(N) / (N - 1))


def traf(x, lw):
    r"""Calculate traf window function

    .. math::
        \mathrm{traf}  &=  (f1 * (f1 + f2)) / (f1^{2} + f2^{2}) &

               f1(t)   &=  \exp(-t * \pi * \mathrm{linewidth[0]}) &

               f2(t)   &=  \exp((t - T) * \pi * \mathrm{linewidth[1]}) &


    Args:
        x (array_like): vector of points
        lw (str): linewidth of traficant window

    Returns:
        ndarray: traf window function
    """
    T2 = 1.0 / (np.pi * lw)
    t = x
    T = np.max(t)
    E = np.exp(-1 * t / T2)
    e = np.exp(-1 * (T - t) / T2)
    return E * (E + e) / (E**2 + e**2)


def hamming(x):
    r"""Calculate hamming window function

    .. math::
        \mathrm{hamming} = 0.53836 + 0.46164\cos(\pi * n / (N-1))

    Args:
        x (array_like): vector of points
        N(int): number of points to return in window function

    Returns:
        ndarray: hamming window function
    """
    N = _handle_array(x)

    return 0.53836 + 0.46164 * np.cos(1.0 * np.pi * np.arange(N) / (N - 1))


# FIX -> Function does not look correct
def lorentz_gauss(x, exp_lw, gauss_lw, gaussian_max=0):
    r"""Calculate lorentz-gauss window function

    .. math::
        \mathrm{lorentz\_gauss} &=  \exp(L -  G^{2}) &

           L(t)    &=  \pi * \mathrm{linewidth[0]} * t &

           G(t)    &=  0.6\pi * \mathrm{linewidth[1]} * (\mathrm{gaussian\_max} * (N - 1) - t) &


    Args:
        x (array_like): vector of points
        N(int): number of points to return in window function
        exp_lw (int or float): exponential linewidth
        gauss_lw (int or float): gaussian linewidth
        gaussian_max (int): location of maximum in gaussian window

    Returns:
        array: gauss_lorentz window function
    """

    N = len(x)
    expo = np.pi * x * exp_lw
    gaus = 0.6 * np.pi * gauss_lw * (gaussian_max * (N - 1) - x)
    return np.exp(expo - gaus**2).reshape(N)


def sin2(x):
    r"""Calculate sin-squared window function

    .. math::
        \sin^{2}  =  \cos((-0.5\pi * n / (N - 1)) + \pi)^{2}

    Args:
        x (array_like): vector of points
        N(int): number of points to return in window function

    Returns:
        array: sin-squared window function
    """
    N = _handle_array(x)

    return np.cos((-0.5 * np.pi * np.arange(N) / (N - 1)) + np.pi) ** 2
