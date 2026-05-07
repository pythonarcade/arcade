import pytest

from arcade.gui import UIDummy
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout, UIGridLayout


def test_get_child_data_returns_correct_dict(window):
    """get_child_data() should return the kwargs dict passed to add()."""
    layout = UIAnchorLayout(width=500, height=500, size_hint=None)
    child = UIDummy(width=100, height=100)
    layout.add(child, anchor_x="left", align_x=50, anchor_y="top", align_y=-10)

    data = layout.get_child_data(child)

    assert data is not None
    assert data["anchor_x"] == "left"
    assert data["align_x"] == 50
    assert data["anchor_y"] == "top"
    assert data["align_y"] == -10


def test_get_child_data_unknown_widget_returns_none(window):
    """get_child_data() should return None for a widget not in the layout."""
    layout = UIAnchorLayout(width=500, height=500, size_hint=None)
    stranger = UIDummy(width=50, height=50)

    assert layout.get_child_data(stranger) is None


def test_get_child_data_modification_affects_layout(window):
    """Modifying the returned dict should change positioning on next do_layout()."""
    layout = UIAnchorLayout(x=0, y=0, width=500, height=500, size_hint=None)
    child = UIDummy(width=100, height=100)
    layout.add(child, anchor_x="left", align_x=0, anchor_y="bottom", align_y=0)

    layout.do_layout()
    original_left = child.left

    data = layout.get_child_data(child)
    data["align_x"] = 50
    layout.do_layout()

    assert child.left == original_left + 50


def test_get_child_entry_returns_first_child(window):
    """get_child_entry(0) should return the first added child and its data."""
    layout = UIAnchorLayout(width=500, height=500, size_hint=None)
    first = UIDummy(width=100, height=100)
    second = UIDummy(width=100, height=100)
    layout.add(first, anchor_x="left")
    layout.add(second, anchor_x="right")

    child, data = layout.get_child_entry(0)

    assert child is first
    assert data["anchor_x"] == "left"


def test_get_child_entry_negative_index(window):
    """get_child_entry(-1) should return the last child."""
    layout = UIAnchorLayout(width=500, height=500, size_hint=None)
    first = UIDummy(width=100, height=100)
    last = UIDummy(width=100, height=100)
    layout.add(first, anchor_x="left")
    layout.add(last, anchor_x="right")

    child, data = layout.get_child_entry(-1)

    assert child is last
    assert data["anchor_x"] == "right"


def test_get_child_entry_out_of_range_raises(window):
    """get_child_entry() should raise IndexError for out-of-range indices."""
    layout = UIAnchorLayout(width=500, height=500, size_hint=None)
    layout.add(UIDummy(width=50, height=50))

    with pytest.raises(IndexError):
        layout.get_child_entry(5)


def test_works_with_box_layout(window):
    """get_child_data() should work with UIBoxLayout children."""
    layout = UIBoxLayout(width=500, height=500, size_hint=None)
    child = UIDummy(width=100, height=100)
    layout.add(child)

    data = layout.get_child_data(child)
    assert data is not None


def test_works_with_grid_layout(window):
    """get_child_data() should work with UIGridLayout children."""
    layout = UIGridLayout(column_count=2, row_count=2, size_hint=None)
    child = UIDummy(width=100, height=100)
    layout.add(child, column=0, row=0)

    data = layout.get_child_data(child)
    assert data is not None
    assert data["column"] == 0
    assert data["row"] == 0


def test_after_remove_and_readd_returns_new_data(window):
    """After remove() + add(), get_child_data() should return the new data."""
    layout = UIAnchorLayout(width=500, height=500, size_hint=None)
    child = UIDummy(width=100, height=100)

    layout.add(child, anchor_x="left", align_x=10)
    layout.remove(child)
    layout.add(child, anchor_x="right", align_x=99)

    data = layout.get_child_data(child)
    assert data["anchor_x"] == "right"
    assert data["align_x"] == 99
