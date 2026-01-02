"""
Unit tests for utils.py

Can run these tests individually with:
python -m pytest tests/unit/test_utils.py
"""

import arcade
from pytest import approx
from arcade.math import *
from arcade.types import LBWH
import random
import math
import pytest


@pytest.fixture(autouse=True)
def set_random_seed():
    random.seed(42) 
    yield

def test_lerp():
    assert lerp(2.0, 4.0, 0.75) == approx(3.5)


def test_lerp_2d():
    vec = lerp_2d((0.0, 2.0), (8.0, 4.0), 0.25)
    assert vec[0] == approx(2.0)
    assert vec[1] == approx(2.5)
    vec = lerp_2d((0.0, 2.0), (8.0, 4.0), -0.25)
    assert vec[0] == approx(-2.0)
    assert vec[1] == approx(1.5)


def test_lerp_angle_normal():
    assert lerp_angle(0, 90, 0.5) == 45


def test_lerp_angle_backwards():
    assert lerp_angle(90, 0, 0.5) == 45


def test_lerp_angle_loop_around():
    assert lerp_angle(355, 15, 0.5) == 5


def test_lerp_angle_loop_around_backwards():
    assert lerp_angle(10, 350, 0.5) == 0


def test_lerp_angle_equal():
    assert lerp_angle(50, 50, 0.5) == 50


def test_lerp_angle_effectively_equal():
    assert lerp_angle(50, 50 + 360, 0.5) == 50
    assert lerp_angle(50 - 360, 50, 0.5) == 50

    
def test_rand_in_rect():
    rect = LBWH(10.0, 20.0, 30.5, 5.1)
    for _ in range(10):
        x, y = rand_in_rect(rect)
        assert rect.left <= x <= rect.right
        assert rect.bottom <= y <= rect.top
    rect = LBWH(-10.0, -20.0, 30.5, 5.1)
    for _ in range(10):
        x, y = rand_in_rect(rect)
        assert rect.left <= x <= rect.right
        assert rect.bottom <= y <= rect.top


def test_rand_in_rect_zero_size():
    rect = LBWH(0.0, 0.0, 0.0, 0.0)
    x, y = rand_in_rect(rect)
    assert x == 0.0
    assert y == 0.0
    
    
    
    
def test_rand_in_circle():
    center=(0, 0)
    r=10.0
    for _ in range(10):
        x, y = rand_in_circle(center,r)
        distance= math.sqrt((x-center[0])**2+(y-center[1])**2)
        assert distance<=r
    

def test_rand_on_circle():
    center=(10.0, 20.0)
    r=15.5
    for _ in range(10):
        x, y = rand_on_circle(center,r)
        distance= math.sqrt((x-center[0])**2+(y-center[1])**2)
        assert distance==approx(r)
        

def test_rand_on_line():
    
    point1=(-5.5, -2.2)
    point2=(5.2, 14.7)
    m=(point2[1]-point1[1])/(point2[0]-point1[0])
    b=point1[1]-m*point1[0]
    for _ in range(10):
        random_point = rand_on_line((-5.5, -2.2),(5.2, 14.7))
        assert random_point[1] == approx(m*random_point[0]+b)
        
def test_rand_angle_360_deg():
    for _ in range(5):
       angle = rand_angle_360_deg()
       assert 0.0 <= angle <= 360.0
        
   

def test_rand_angle_spread_deg():
    rand_angle_spread_deg(45.0, 5.0)
    angle = 45.0
    spread = 5.0
    for _ in range(5):
       new_angle = rand_angle_spread_deg(angle,spread)
       assert angle - spread <= new_angle <= angle + spread
    


def test_rand_vec_spread_deg():
    rand_vec_spread_deg(-45.0, 5.0, 3.3)
    angle = -45.0
    half = 5.0
    length = 3.3
    for _ in range(200):
        x, y = rand_vec_spread_deg(angle, half, length)  
        mag = math.hypot(x, y)
        assert mag == approx(length, rel=1e-7, abs=1e-7)



def test_rand_vec_magnitude():
    rand_vec_magnitude(30.5, 3.3, 4.4)
    angle = 30.5
    lo = 3.3
    hi = 4.4
    for _ in range(5):
        x,y = rand_vec_magnitude(angle,lo,hi)
        mag = math.hypot(x,y)
        assert lo<= mag <=hi


