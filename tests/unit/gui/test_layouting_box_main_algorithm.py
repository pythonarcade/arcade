from pytest import approx

from arcade.gui import UIWidget
from arcade.gui.widgets.layout import _C, _box_axis_algorithm


def test_constraint_from_widget_no_sh():
    widget = UIWidget(size_hint=None, width=100)

    assert _C.from_widget_width(widget) == _C(hint=0, min=100, max=100)


def test_constraint_from_widget_no_shm():
    widget = UIWidget(size_hint=(1, 1), width=100, size_hint_min=None)

    assert _C.from_widget_width(widget) == _C(hint=1, min=0, max=None)


def test_shw_smaller_1(window):
    # GIVEN
    entries = [
        _C(hint=0.1, min=0, max=None),
        _C(hint=0.1, min=0, max=None),
        _C(hint=0.5, min=0, max=None),
    ]

    # WHEN
    sizes = _box_axis_algorithm(entries, 100)

    # THEN
    assert sizes == [10, 10, 50]


def test_complex_example_with_max_value():
    # GIVEN
    entries = [
        _C(hint=0.2, min=0, max=None),
        _C(hint=0.2, min=0, max=None),
        _C(hint=0.6, min=0, max=50),
    ]

    # WHEN
    sizes = _box_axis_algorithm(entries, 100)

    # THEN
    assert sizes == [20, 20, 50]


def test_complex_example_with_max_value_2():
    # GIVEN
    entries = [
        _C(hint=0.2, min=10, max=10),
        _C(hint=0.2, min=10, max=15),
        _C(hint=0.6, min=10, max=50),
    ]

    # WHEN
    sizes = _box_axis_algorithm(entries, 100)

    # THEN
    assert sizes == [10, 15, 50]


def test_complex_example_with_max_value_hint_above_1():
    # GIVEN
    entries = [
        _C(hint=0.3, min=0, max=None),
        _C(hint=0.2, min=0, max=None),
        _C(hint=0.6, min=0, max=50),
    ]

    # WHEN
    sizes = _box_axis_algorithm(entries, 100)

    # THEN
    assert sum(sizes) == 100
    assert sizes == [30, 20, 50]


def test_complex_example_with_min_value():
    # GIVEN
    entries = [
        _C(hint=0.3, min=0, max=None),
        _C(hint=0.3, min=0, max=None),
        _C(hint=0.1, min=50, max=None),
    ]

    # WHEN
    sizes = _box_axis_algorithm(entries, 100)

    # THEN
    assert sizes == [25, 25, 50]


def test_issue_example_with_min_value():
    # GIVEN
    entries = [
        _C(hint=0.2, min=0, max=None),
        _C(hint=0.2, min=0, max=None),
        _C(hint=0.3, min=20, max=None),
    ]

    # WHEN
    sizes = _box_axis_algorithm(entries, 100)

    # THEN
    assert sizes == [20, 20, 30]


def test_complex_example_hint_above_1():
    # GIVEN
    entries = [
        _C(hint=0.4, min=0, max=None),
        _C(hint=0.4, min=0, max=None),
        _C(hint=0.4, min=0, max=None),
    ]

    # WHEN
    e1, e2, e3 = _box_axis_algorithm(entries, 100)

    # THEN
    assert e1 == approx(33.33, rel=0.01)
    assert e2 == approx(33.33, rel=0.01)
    assert e3 == approx(33.33, rel=0.01)


def test_complex_example_hint_above_1_with_min():
    # GIVEN
    entries = [
        _C(hint=0.4, min=0, max=None),
        _C(hint=0.4, min=0, max=None),
        _C(hint=0.4, min=50, max=None),
    ]

    # WHEN
    sizes = _box_axis_algorithm(entries, 100)

    # THEN
    assert sizes == [25, 25, 50]


def test_more_complex_example():
    # GIVEN
    entries = [
        _C(hint=0.4, min=0, max=None),
        _C(hint=0.4, min=50, max=None),
        _C(hint=0.4, min=50, max=None),
    ]

    # WHEN
    sizes = _box_axis_algorithm(entries, 100)

    # THEN
    assert sizes == [0, 50, 50]


def test_min_greater_total():
    # GIVEN
    entries = [
        _C(hint=0.2, min=10, max=None),
        _C(hint=0.2, min=50, max=None),
        _C(hint=0.2, min=50, max=None),
    ]

    # WHEN
    sizes = _box_axis_algorithm(entries, 100)

    # THEN
    assert sizes == [10, 50, 50]


def test_size_hint_is_0():
    # GIVEN
    entries = [
        _C(hint=0, min=0, max=None),
        _C(hint=0.5, min=50, max=None),
        _C(hint=0.5, min=50, max=None),
    ]

    # WHEN
    sizes = _box_axis_algorithm(entries, 100)

    # THEN
    assert sizes == [0, 50, 50]


def test_example_without_hint():
    # GIVEN
    entries = [
        _C(hint=0, min=10, max=None),
        _C(hint=0, min=50, max=None),
        _C(hint=0, min=50, max=None),
    ]

    # WHEN
    sizes = _box_axis_algorithm(entries, 100)

    # THEN
    assert sizes == [10, 50, 50]


def test_example_grow_relative_to_size_hint():
    # GIVEN
    entries = [
        _C(hint=1, min=25, max=None),
        _C(hint=0.5, min=25, max=None),
    ]

    # WHEN
    e1, e2 = _box_axis_algorithm(entries, 100)

    # THEN
    assert [int(e1), int(e2)] == [
        66,
        33,
    ]


def test_example_grow_relative_to_size_hint_no_min():
    # GIVEN
    entries = [
        _C(hint=1, min=0, max=None),
        _C(hint=0.5, min=0, max=None),
    ]

    # WHEN
    e1, e2 = _box_axis_algorithm(entries, 100)

    # THEN
    assert [int(e1), int(e2)] == [
        66,
        33,
    ]


def test_example_grow_relative_to_size_hint_huge_min():
    # GIVEN
    entries = [
        _C(hint=0.75, min=0, max=None),
        _C(hint=0.5, min=80, max=None),
    ]

    # WHEN
    e1, e2 = _box_axis_algorithm(entries, 100)

    # THEN
    assert [int(e1), int(e2)] == [
        20,
        80,
    ]


def test_example_grow_relative_to_size_hint_huge_min_2():
    # GIVEN
    entries = [
        _C(hint=1, min=0, max=None),
        _C(hint=0.5, min=0, max=None),
        _C(hint=0.5, min=70, max=None),
    ]

    # WHEN
    e1, e2, e3 = _box_axis_algorithm(entries, 100)

    # THEN
    assert [
        int(e1),
        int(e2),
        int(e3),
    ] == [
        20,
        10,
        70,
    ]


def test_enforced_min_size():
    # GIVEN
    entries = [
        _C(hint=0, min=30, max=None),
        _C(hint=1, min=30, max=None),
    ]

    # WHEN
    e1, e2 = _box_axis_algorithm(entries, 100)

    # THEN
    assert [int(e1), int(e2)] == [
        30,
        70,
    ]
