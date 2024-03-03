from arcade.gui import UIDummy, UIManager, UIBoxLayout, UIAnchorLayout
from arcade.gui.widgets import Rect
from arcade.gui.widgets.layout import UIGridLayout


def test_place_widget(window):
    dummy1 = UIDummy(width=100, height=100)
    dummy2 = UIDummy(width=100, height=100)
    dummy3 = UIDummy(width=100, height=100)
    dummy4 = UIDummy(width=100, height=100)

    subject = UIGridLayout(column_count=2, row_count=2)

    subject.add(dummy1, 0, 0)
    subject.add(dummy2, 0, 1)
    subject.add(dummy3, 1, 0)
    subject.add(dummy4, 1, 1)

    subject.rect = Rect(0, 0, *subject.size_hint_min)
    subject.do_layout()

    # check that do_layout doesn't manipulate the rect
    assert subject.rect == (0, 0, 200, 200)

    assert dummy1.position == (0, 100)
    assert dummy2.position == (0, 0)
    assert dummy3.position == (100, 100)
    assert dummy4.position == (100, 0)


def test_can_handle_empty_cells(window):
    dummy1 = UIDummy(width=100, height=100)

    subject = UIGridLayout(column_count=2, row_count=2)

    subject.add(dummy1, 0, 0)

    subject.rect = Rect(0, 0, *subject.size_hint_min)
    subject.do_layout()

    # check that do_layout doesn't manipulate the rect
    assert subject.rect == (0, 0, 100, 100)

    assert dummy1.position == (0, 0)


def test_place_widget_with_different_sizes(window):
    dummy1 = UIDummy(width=50, height=100)
    dummy2 = UIDummy(width=100, height=100)
    dummy3 = UIDummy(width=100, height=50)
    dummy4 = UIDummy(width=50, height=50)

    subject = UIGridLayout(column_count=2, row_count=2)

    subject.add(dummy1, 0, 0)
    subject.add(dummy2, 0, 1)
    subject.add(dummy3, 1, 0)
    subject.add(dummy4, 1, 1)

    subject.rect = Rect(0, 0, *subject.size_hint_min)
    subject.do_layout()

    assert subject.rect == (0, 0, 200, 200)

    assert dummy1.position == (25, 100)
    assert dummy2.position == (0, 0)
    assert dummy3.position == (100, 125)
    assert dummy4.position == (125, 25)


def test_place_widget_within_content_rect(window):
    dummy1 = UIDummy(width=100, height=100)

    subject = UIGridLayout(column_count=1, row_count=1).with_padding(left=10, bottom=20)

    subject.add(dummy1, 0, 0)

    assert subject.size_hint_min == (110, 120)

    subject.rect = Rect(0, 0, *subject.size_hint_min)
    subject.do_layout()

    assert dummy1.position == (10, 20)


def test_place_widgets_with_col_row_span(window):
    dummy1 = UIDummy(width=100, height=100)
    dummy2 = UIDummy(width=100, height=100)
    dummy3 = UIDummy(width=100, height=100)
    dummy4 = UIDummy(width=100, height=100)
    dummy5 = UIDummy(width=200, height=100)
    dummy6 = UIDummy(width=100, height=200)

    subject = UIGridLayout(
        column_count=3,
        row_count=3,
    )

    subject.add(dummy1, 0, 0)
    subject.add(dummy2, 0, 1)
    subject.add(dummy3, 1, 0)
    subject.add(dummy4, 1, 1)
    subject.add(dummy5, 0, 2, col_span=2)
    subject.add(dummy6, 2, 0, row_span=3)

    subject.rect = Rect(0, 0, *subject.size_hint_min)
    subject.do_layout()

    assert dummy1.position == (0, 200)
    assert dummy2.position == (0, 100)
    assert dummy3.position == (100, 200)
    assert dummy4.position == (100, 100)
    assert dummy5.position == (0, 0)
    assert dummy6.position == (200, 50)


def test_place_widgets_with_col_row_span_and_spacing(window):
    dummy1 = UIDummy(width=100, height=100)
    dummy2 = UIDummy(width=100, height=100)
    dummy3 = UIDummy(width=100, height=100)
    dummy4 = UIDummy(width=100, height=100)
    dummy5 = UIDummy(width=220, height=100)

    subject = UIGridLayout(
        column_count=2,
        row_count=3,
        horizontal_spacing=20,
    )

    subject.add(dummy1, 0, 0)
    subject.add(dummy2, 0, 1)
    subject.add(dummy3, 1, 0)
    subject.add(dummy4, 1, 1)
    subject.add(dummy5, 0, 2, col_span=2)

    subject.rect = Rect(0, 0, *subject.size_hint_min)
    subject.do_layout()

    assert dummy1.position == (10, 200)
    assert dummy2.position == (10, 100)
    assert dummy3.position == (130, 200)
    assert dummy4.position == (130, 100)
    assert dummy5.position == (10, 0)


def test_fit_content_by_default(window):
    subject = UIGridLayout(
        column_count=1,
        row_count=1,
    )

    assert subject.size_hint == (0, 0)


def test_adjust_children_size_relative(window):
    dummy1 = UIDummy(width=100, height=100)
    dummy2 = UIDummy(width=50, height=50, size_hint=(0.75, 0.75))
    dummy3 = UIDummy(
        width=100, height=100, size_hint=(0.5, 0.5), size_hint_min=(60, 60)
    )
    dummy4 = UIDummy(width=100, height=100)

    subject = UIGridLayout(
        column_count=2,
        row_count=2,
    )

    subject.add(dummy1, 0, 0)
    subject.add(dummy2, 0, 1)
    subject.add(dummy3, 1, 0)
    subject.add(dummy4, 1, 1)

    subject.rect = Rect(0, 0, *subject.size_hint_min)
    subject.do_layout()

    # check that do_layout doesn't manipulate the rect
    assert subject.rect == (0, 0, 200, 200)

    assert dummy1.size == (100, 100)
    assert dummy2.size == (75, 75)
    assert dummy3.size == (60, 60)
    assert dummy4.size == (100, 100)


def test_does_not_adjust_children_without_size_hint(window):
    dummy1 = UIDummy(width=100, height=100)
    dummy2 = UIDummy(width=50, height=50, size_hint=(0.75, None))
    dummy3 = UIDummy(width=50, height=50, size_hint=(None, 0.75))
    dummy4 = UIDummy(width=100, height=100)

    subject = UIGridLayout(
        column_count=2,
        row_count=2,
    )

    subject.add(dummy1, 0, 0)
    subject.add(dummy2, 0, 1)
    subject.add(dummy3, 1, 0)
    subject.add(dummy4, 1, 1)

    subject.rect = Rect(0, 0, *subject.size_hint_min)
    subject.do_layout()

    # check that do_layout doesn't manipulate the rect
    assert subject.rect == (0, 0, 200, 200)

    assert dummy1.size == (100, 100)
    assert dummy2.size == (75, 50)
    assert dummy3.size == (50, 75)
    assert dummy4.size == (100, 100)


def test_size_hint_and_spacing(window):
    dummy1 = UIDummy(width=100, height=100)

    subject = UIGridLayout(
        column_count=2,
        row_count=2,
        horizontal_spacing=10,
        vertical_spacing=10,
    )

    subject.add(dummy1, 0, 0)

    subject.rect = Rect(0, 0, *subject.size_hint_min)
    subject.do_layout()

    assert dummy1.size == (100, 100)

    subject.do_layout()
    assert dummy1.size == (100, 100)


def test_empty_cells(window):
    dummy1 = UIDummy(width=100, height=100)

    subject = UIGridLayout(
        column_count=3,
        row_count=3,
    )

    subject.add(dummy1, 2, 2)

    subject.rect = Rect(0, 0, *subject.size_hint_min)
    subject.do_layout()

    assert dummy1.position == (0, 0)


def test_nested_grid_layouts(window):
    ui = UIManager()
    outer = UIGridLayout(row_count=1, column_count=1)
    inner = UIGridLayout(row_count=1, column_count=1)

    inner.add(UIDummy(), 0, 0)
    outer.add(inner, 0, 0)
    ui.add(outer)

    ui.execute_layout()

    assert inner.rect.size == (100, 100)
    assert outer.rect.size == (100, 100)


def test_nested_box_layouts(window):
    ui = UIManager()
    outer = UIGridLayout(row_count=1, column_count=1)
    inner = UIBoxLayout()

    inner.add(UIDummy())
    outer.add(inner, 0, 0)
    ui.add(outer)

    ui.execute_layout()

    assert inner.rect.size == (100, 100)
    assert outer.rect.size == (100, 100)


def test_nested_anchor_layouts(window):
    ui = UIManager()
    outer = UIGridLayout(row_count=1, column_count=1)
    inner = UIAnchorLayout(size_hint_min=(100, 100))

    outer.add(inner, 0, 0)
    ui.add(outer)

    ui.execute_layout()

    assert inner.rect.size == (100, 100)
    assert outer.rect.size == (100, 100)


def test_update_size_hint_min_on_child_size_change(window):
    ui = UIManager()
    grid = UIGridLayout(row_count=1, column_count=1)
    dummy = UIDummy(size_hint_min=(100, 100), size_hint=(0, 0))

    grid.add(dummy, 0, 0)
    ui.add(grid)

    dummy.size_hint_min = (200, 200)
    ui.execute_layout()

    assert dummy.rect.size == (200, 200)
    assert grid.rect.size == (200, 200)
