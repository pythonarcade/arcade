from typing import Tuple


def _lerp_2D(_p1: Tuple[float, float], _p2: Tuple[float, float], _t: float):
    _x1, _y1 = _p1
    _x2, _y2 = _p2

    return _x1 + _t*(_x2 - _x1), _y1 + _t*(_y2 - _y1)


def _lerp_3D(_p1: Tuple[float, float, float], _p2: Tuple[float, float, float], _t: float):
    _x1, _y1, _z1 = _p1
    _x2, _y2, _z2 = _p2

    return _x1 + _t*(_x2 - _x1), _y1 + _t*(_y2 - _y1), _z1 + _t*(_z2 - _z1)


def _quad_2D(_p1: Tuple[float, float], _p2: Tuple[float, float],
             _p3: Tuple[float, float],
             _t: float):
    _x1, _y1 = _p1
    _x2, _y2 = _p2
    _x3, _y3 = _p3
    _t2 = _t**2.0

    return (
        _x1*(1.0 - 2.0*_t + _t2) + 2.0*_x2*(_t - _t2) + _x3*_t2,
        _y1*(1.0 - 2.0*_t + _t2) + 2.0*_y2*(_t - _t2) + _y3*_t2
    )


def _quad_3D(_p1: Tuple[float, float, float], _p2: Tuple[float, float, float],
             _p3: Tuple[float, float, float],
             _t: float):
    _x1, _y1, _z1 = _p1
    _x2, _y2, _z2 = _p2
    _x3, _y3, _z3 = _p3
    _t2 = _t**2.0

    return (
        _x1*(1.0 - 2.0*_t + _t2) + 2.0*_x2*(_t - _t2) + _x3*_t2,
        _y1*(1.0 - 2.0*_t + _t2) + 2.0*_y2*(_t - _t2) + _y3*_t2,
        _z1*(1.0 - 2.0*_t + _t2) + 2.0*_z2*(_t - _t2) + _z3*_t2
    )


def _cubic_2D(_p1: Tuple[float, float], _p2: Tuple[float, float],
              _p3: Tuple[float, float], _p4: Tuple[float, float],
              _t: float):
    _x1, _y1 = _p1
    _x2, _y2 = _p2
    _x3, _y3 = _p3
    _x4, _y4 = _p4
    _t2, _t3 = _t**2.0, _t**3.0

    return (
        _x1*(-_t3 + 3.0*_t2 - 3.0*_t + 1.0) + _x2*(3.0*_t3 - 6.0*_t2 + 3.0*_t) + 3.0*_x3*(-_t3 + _t2) + _x4*_t3,
        _y1*(-_t3 + 3.0*_t2 - 3.0*_t + 1.0) + _y2*(3.0*_t3 - 6.0*_t2 + 3.0*_t) + 3.0*_y3*(-_t3 + _t2) + _y4*_t3
    )


def _cubic_3D(_p1: Tuple[float, float, float], _p2: Tuple[float, float, float],
              _p3: Tuple[float, float, float], _p4: Tuple[float, float, float],
              _t: float):
    _x1, _y1, _z1 = _p1
    _x2, _y2, _z2 = _p2
    _x3, _y3, _z3 = _p3
    _x4, _y4, _z4 = _p4
    _t2, _t3 = _t**2.0, _t**3.0

    return (
        _x1*(-_t3 + 3.0*_t2 - 3.0*_t + 1.0) + _x2*(3.0*_t3 - 6.0*_t2 + 3.0*_t) + 3.0*_x3*(-_t3 + _t2) + _x4*_t3,
        _y1*(-_t3 + 3.0*_t2 - 3.0*_t + 1.0) + _y2*(3.0*_t3 - 6.0*_t2 + 3.0*_t) + 3.0*_y3*(-_t3 + _t2) + _y4*_t3,
        _z1*(-_t3 + 3.0*_t2 - 3.0*_t + 1.0) + _z2*(3.0*_t3 - 6.0*_t2 + 3.0*_t) + 3.0*_z3*(-_t3 + _t2) + _z4*_t3
    )


def _b_spline_2D(_p1: Tuple[float, float], _p2: Tuple[float, float],
                 _p3: Tuple[float, float], _p4: Tuple[float, float],
                 _t: float):
    _x1, _y1 = _p1
    _x2, _y2 = _p2
    _x3, _y3 = _p3
    _x4, _y4 = _p4
    _t2, _t3 = _t**2.0, _t**3.0

    return (
        (1/6)*(
            _x1*(-_t3 + 3.0*_t2 - 3.0*_t + 1.0) +
            _x2*(3.0*_t3 - 6.0*_t2 + 4.0) +
            _x3*(-3.0*_t3 + 3*_t2 + 3.0*_t + 1.0) +
            _x4*_t3
        ),
        (1/6)*(
            _y1*(-_t3 + 3.0*_t2 - 3.0*_t + 1.0) +
            _y2*(3.0*_t3 - 6.0*_t2 + 4.0) +
            _y3*(-3.0*_t3 + 3*_t2 + 3.0*_t + 1.0) +
            _y4*_t3
        )
    )


def _b_spline_3D(_p1: Tuple[float, float, float], _p2: Tuple[float, float, float],
                 _p3: Tuple[float, float, float], _p4: Tuple[float, float, float],
                 _t: float):
    _x1, _y1, _z1 = _p1
    _x2, _y2, _z2 = _p2
    _x3, _y3, _z3 = _p3
    _x4, _y4, _z4 = _p4
    _t2, _t3 = _t**2.0, _t**3.0

    return (
        (1 / 6)*(
                _x1*(-_t3 + 3.0*_t2 - 3.0*_t + 1.0) +
                _x2*(3.0*_t3 - 6.0*_t2 + 4.0) +
                _x3*(-3.0*_t3 + 3*_t2 + 3.0*_t + 1.0) +
                _x4*_t3
        ),
        (1 / 6)*(
                _y1*(-_t3 + 3.0*_t2 - 3.0*_t + 1.0) +
                _y2*(3.0*_t3 - 6.0*_t2 + 4.0) +
                _y3*(-3.0*_t3 + 3*_t2 + 3.0*_t + 1.0) +
                _y4*_t3
        ),
        (1 / 6)*(
                _y1*(-_t3 + 3.0*_t2 - 3.0*_t + 1.0) +
                _y2*(3.0*_t3 - 6.0*_t2 + 4.0) +
                _y3*(-3.0*_t3 + 3*_t2 + 3.0*_t + 1.0) +
                _y4*_t3
        )
    )


__all__ = {
    'SplineController'
}


class SplineController:

    pass
