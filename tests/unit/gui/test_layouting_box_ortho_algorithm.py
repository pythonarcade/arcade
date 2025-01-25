from arcade.gui.widgets.layout import _C, _box_axis_algorithm, _box_orthogonal_algorithm


def test_simple_values(window):
    # GIVEN
    entries = [
        _C(hint=0.1, min=0, max=None),
        _C(hint=0.1, min=0, max=None),
        _C(hint=0.5, min=0, max=None),
    ]

    # WHEN
    positions = _box_orthogonal_algorithm(entries, 100)

    # THEN
    assert positions == [10, 10, 50]


def test_issue_example_with_min_value():
    # GIVEN
    entries = [
        _C(hint=0.2, min=0, max=None),
        _C(hint=0.2, min=0, max=None),
        _C(hint=0.3, min=40, max=None),
    ]

    # WHEN
    positions = _box_orthogonal_algorithm(entries, 100)

    # THEN
    assert positions == [20, 20, 40]


def test_issue_example_with_max_value():
    # GIVEN
    entries = [
        _C(hint=0.2, min=0, max=None),
        _C(hint=0.2, min=0, max=None),
        _C(hint=1, min=0, max=50),
    ]

    # WHEN
    positions = _box_orthogonal_algorithm(entries, 100)

    # THEN
    assert positions == [20, 20, 50]
