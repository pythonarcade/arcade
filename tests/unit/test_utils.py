"""
Unit tests for utils.py

Can run these tests individually with:
python -m pytest tests/unit/test_utils.py
"""
from typing import Callable, Any

from arcade import utils


class _Dummy:
    ...


def fn_returns_expect_for_nonstr_iterables(fn: Callable[[Any], bool], expect: bool):
    assert fn((1, 2)) == expect
    assert fn([1, 2]) == expect
    assert fn(range(3)) == expect

    # empty iterables are still iterables
    assert fn(tuple()) == expect
    assert fn([]) == expect
    assert fn(iter(tuple())) == expect
    assert fn(set()) == expect


def fn_returns_expect_for_noniterables(fn: Callable[[Any], bool], expect: bool):
    assert fn(1) == expect  # Numbers
    assert fn(complex(1,2)) == expect  # Numbers part 2: complex is not iterable like pyglet vecs
    assert fn(type) == expect  # types
    assert fn(_Dummy()) == expect  # Instances
    assert fn(print) == expect  # Functions


def test_is_iterable():
    assert utils.is_iterable("test")
    fn_returns_expect_for_nonstr_iterables(utils.is_iterable, True)
    fn_returns_expect_for_noniterables(utils.is_iterable, False)


def test_is_str_or_noniterable():
    assert utils.is_str_or_noniterable("test")
    fn_returns_expect_for_nonstr_iterables(utils.is_str_or_noniterable, False)
    fn_returns_expect_for_noniterables(utils.is_str_or_noniterable, True)


def test_grow_sequence():
    destination = []
    utils.grow_sequence(destination, "ab", append_if=lambda _: False)
    assert len(destination) == 2
    assert destination[0] == "a"
    assert destination[1] == "b"

    big = "this should be added as one big string"
    utils.grow_sequence(destination, big, append_if=lambda _: True)
    assert len(destination) == 3
    assert destination[0] == "a"
    assert destination[1] == "b"
    assert destination[2] == big


def test_is_nonstr_or_iterable():
    assert not utils.is_nonstr_iterable("test")
    fn_returns_expect_for_nonstr_iterables(utils.is_nonstr_iterable, True)
    fn_returns_expect_for_noniterables(utils.is_nonstr_iterable, False)


def test_is_raspberry_pi():
    assert isinstance(utils.is_raspberry_pi(), bool)


def test_get_raspberry_pi_info():
    is_raspi, arch, model = utils.get_raspberry_pi_info()
    assert isinstance(is_raspi, bool)
    assert isinstance(arch, str)
    assert isinstance(model, str)
