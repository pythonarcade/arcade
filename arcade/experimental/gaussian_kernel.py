"""
Gaussian kernel calculator
Adapted from:
https://observablehq.com/@jobleonard/gaussian-kernel-calculater
"""

import math

SQRT2 = math.sqrt(2)


def erf(x: float):
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911

    t = 1.0 / (1.0 + p * abs(x))
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)

    return math.copysign(1, x) * y


def def_int_gaussian(x: float, mu: float, sigma: float):
    return 0.5 * erf((x - mu) / (SQRT2 * sigma))


def gaussian_kernel(kernel_size: int = 5, sigma: float = 1, mu: float = 0, step: int = 1):
    end = 0.5 * kernel_size
    start = -end
    coeff = []
    sum = 0
    x = start
    last_int = def_int_gaussian(x, mu, sigma)
    while x < end:
        x += step
        new_int = def_int_gaussian(x, mu, sigma)
        c = new_int - last_int
        coeff.append(c)
        sum += c
        last_int = new_int

    # normalize
    sum_norm = 1 / sum
    for i in range(len(coeff)):
        coeff[i] *= sum_norm

    return coeff
