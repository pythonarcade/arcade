import math
import random
from pymunk import Vec2d

def lerp(v1: float, v2: float, u: float) -> float:
    """linearly interpolate between two values"""
    return v1 + ((v2 - v1) * u)

def vec_lerp(v1: Vec2d, v2: Vec2d, u: float) -> Vec2d:
    return Vec2d(
        lerp(v1.x, v2.x, u),
        lerp(v1.y, v2.y, u)
    )

def rand_in_rect(bottom_left: Vec2d, width: float, height: float) -> Vec2d:
    return Vec2d(
        random.uniform(bottom_left.x, bottom_left.x + width),
        random.uniform(bottom_left.y, bottom_left.y + height)
    )

def rand_in_circle(center: Vec2d, radius: float) -> Vec2d:
    """Generate a point in a circle, or can think of it as a vector pointing a random direction with a random magnitude <= radius
    Reference: http://stackoverflow.com/a/30564123
    Note: This algorithm returns a higher concentration of points around the center of the circle"""
    # random angle
    angle = 2 * math.pi * random.random()
    # random radius
    r = radius * random.random()
    # calculating coordinates
    return Vec2d(
        r * math.cos(angle) + center.x,
        r * math.sin(angle) + center.y
    )

def rand_on_circle(center: Vec2d, radius: float) -> Vec2d:
    """Note: by passing a random value in for float, you can achieve what rand_in_circle() does"""
    angle = 2 * math.pi * random.random()
    return Vec2d(
        radius * math.cos(angle) + center.x,
        radius * math.sin(angle) + center.y
    )

def rand_on_line(pos1: Vec2d, pos2: Vec2d) -> Vec2d:
    u = random.uniform(0.0, 1.0)
    return vec_lerp(pos1, pos2, u)

def rand_angle_360_deg():
    return random.uniform(0.0, 360.0)

def rand_angle_spread_deg(angle: float, half_angle_spread: float) -> float:
    s = random.uniform(-half_angle_spread, half_angle_spread)
    return angle + s

def rand_vec_spread_deg(angle: float, half_angle_spread: float, length: float) -> Vec2d:
    a = rand_angle_spread_deg(angle, half_angle_spread)
    v = Vec2d().ones()
    v.length = length
    v.angle_degrees = a
    return v

def rand_vec_magnitude(angle: float, lo_magnitude: float, hi_magnitude: float) -> Vec2d:
    mag = random.uniform(lo_magnitude, hi_magnitude)
    v = Vec2d().ones()
    v.length = mag
    v.angle_degrees = angle
    return v

