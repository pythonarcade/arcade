from pyglet.math import Vec2

from arcade import LBWH
from arcade.gui import UIAnchorLayout, UIBoxLayout, UIDummy, UIManager
from arcade.gui.widgets.layout import UIGridLayout


def test_place_widget(ui):
    dummy1 = UIDummy(width=100, height=100)
    dummy2 = UIDummy(width=100, height=100)
    dummy3 = UIDummy(width=100, height=100)
    dummy4 = UIDummy(width=100, height=100)

    subject = UIGridLayout(column_count=2, row_count=2)

    subject.add(dummy1, 0, 0)
    subject.add(dummy2, 0, 1)
    subject.add(dummy3, 1, 0)
    subject.add(dummy4, 1, 1)

    ui.add(subject)
    ui.execute_layout()

    # check that do_layout doesn't manipulate the rect
    assert subject.rect == LBWH(0, 0, 200, 200)

    assert dummy1.position == Vec2(0, 100)
    assert dummy2.position == Vec2(0, 0)
    assert dummy3.position == Vec2(100, 100)
    assert dummy4.position == Vec2(100, 0)


def test_can_handle_empty_cells(ui):
    dummy1 = UIDummy(width=100, height=100)

    subject = UIGridLayout(column_count=2, row_count=2)

    subject.add(dummy1, 0, 0)

    ui.add(subject)
    ui.execute_layout()

    # check that do_layout doesn't manipulate the rect
    assert subject.rect == LBWH(0, 0, 100, 100)

    assert dummy1.position == Vec2(0, 0)


def test_place_widget_with_different_sizes(ui):
    dummy1 = UIDummy(width=50, height=100)
    dummy2 = UIDummy(width=100, height=100)
    dummy3 = UIDummy(width=100, height=50)
    dummy4 = UIDummy(width=50, height=50)

    subject = UIGridLayout(column_count=2, row_count=2)

    subject.add(dummy1, 0, 0)
    subject.add(dummy2, 0, 1)
    subject.add(dummy3, 1, 0)
    subject.add(dummy4, 1, 1)

    ui.add(subject)
    ui.execute_layout()

    assert subject.rect == LBWH(0, 0, 200, 200)

    assert dummy1.position == Vec2(25, 100)
    assert dummy2.position == Vec2(0, 0)
    assert dummy3.position == Vec2(100, 125)
    assert dummy4.position == Vec2(125, 25)


def test_place_widget_within_content_rect(ui):
    dummy1 = UIDummy(width=100, height=100)

    subject = UIGridLayout(column_count=1, row_count=1).with_padding(left=10, bottom=20)

    subject.add(dummy1, 0, 0)

    ui.add(subject)
    ui.execute_layout()

    assert subject.size_hint_min == (110, 120)
    assert dummy1.position == Vec2(10, 20)


def test_place_widgets_with_col_row_span(ui):
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
    subject.add(dummy5, 0, 2, column_span=2)
    subject.add(dummy6, 2, 0, row_span=3)

    ui.add(subject)
    ui.execute_layout()

    assert dummy1.position == Vec2(0, 200)
    assert dummy2.position == Vec2(0, 100)
    assert dummy3.position == Vec2(100, 200)
    assert dummy4.position == Vec2(100, 100)
    assert dummy5.position == Vec2(0, 0)
    assert dummy6.position == Vec2(200, 50)


def test_place_widgets_with_col_row_span_and_spacing(ui):
    """
      col1  col2
    +-----+-----+
    |  1  |  2  |
    +-----+-----+
    |  3  |  4  |
    +-----+-----+
    |     6     |
    +-----+-----+

    col1 width: 100
    col2 width: 100
    """
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
    subject.add(dummy2, 1, 0)
    subject.add(dummy3, 0, 1)
    subject.add(dummy4, 1, 1)
    subject.add(dummy5, 0, 2, column_span=2)

    ui.add(subject)
    ui.execute_layout()

    assert subject.rect.size == (220, 300)
    assert dummy1.position == Vec2(0, 200)
    assert dummy2.position == Vec2(120, 200)
    assert dummy3.position == Vec2(0, 100)
    assert dummy4.position == Vec2(120, 100)
    assert dummy5.position == Vec2(0, 0)


def test_fit_content_by_default(ui):
    subject = UIGridLayout(
        column_count=1,
        row_count=1,
    )

    assert subject.size_hint == (0, 0)


def test_adjust_children_size_relative(ui):
    dummy1 = UIDummy(width=50, height=50)  # fix size
    dummy2 = UIDummy(width=50, height=50, size_hint=(0.75, 0.75))  # shrinks
    dummy3 = UIDummy(
        width=100, height=100, size_hint=(0.3, 0.3), size_hint_min=(60, 60)
    )  # shrinks to 60,60
    dummy4 = UIDummy(width=10, height=10)  # fix size

    subject = UIGridLayout(
        column_count=2,
        row_count=2,
    )

    subject.add(dummy1, 0, 0)
    subject.add(dummy2, 0, 1)
    subject.add(dummy3, 1, 0)
    subject.add(dummy4, 1, 1)

    ui.add(subject)
    ui.execute_layout()

    assert subject.rect.size == (110, 70)
    assert dummy1.size == Vec2(50, 50)
    assert dummy2.size == Vec2(
        50,  # width: 75% of 110 is 82, but cell is only 50, so it should be 50
        10,  # height: 75% of 70 is 52, but cell is only 10, so it should be 10
    )
    assert dummy3.size == Vec2(60, 60)
    assert dummy4.size == Vec2(10, 10)


def test_does_not_adjust_children_without_size_hint(ui):
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

    ui.add(subject)
    ui.execute_layout()

    # check that do_layout doesn't manipulate the rect
    assert subject.rect == LBWH(0, 0, 200, 200)

    assert dummy1.size == Vec2(100, 100)
    assert dummy2.size == Vec2(100, 50)
    assert dummy3.size == Vec2(50, 100)
    assert dummy4.size == Vec2(100, 100)


def test_size_hint_and_spacing(ui):
    dummy1 = UIDummy(width=100, height=100)

    subject = UIGridLayout(
        column_count=2,
        row_count=2,
        horizontal_spacing=10,
        vertical_spacing=10,
    )

    subject.add(dummy1, 0, 0)

    ui.add(subject)
    ui.execute_layout()

    assert dummy1.size == Vec2(100, 100)

    subject.do_layout()
    assert dummy1.size == Vec2(100, 100)


def test_empty_cells(ui):
    dummy1 = UIDummy(width=100, height=100)

    subject = UIGridLayout(
        column_count=3,
        row_count=3,
    )

    subject.add(dummy1, 2, 2)

    ui.add(subject)
    ui.execute_layout()

    assert dummy1.position == Vec2(0, 0)


def test_nested_grid_layouts(ui):
    outer = UIGridLayout(row_count=1, column_count=1)
    inner = UIGridLayout(row_count=1, column_count=1)

    inner.add(UIDummy(), 0, 0)
    outer.add(inner, 0, 0)
    ui.add(outer)

    ui.execute_layout()

    assert inner.rect.size == Vec2(100, 100)
    assert outer.rect.size == Vec2(100, 100)


def test_nested_box_layouts(ui):
    outer = UIGridLayout(row_count=1, column_count=1)
    inner = UIBoxLayout()

    inner.add(UIDummy())
    outer.add(inner, 0, 0)
    ui.add(outer)

    ui.execute_layout()

    assert inner.rect.size == Vec2(100, 100)
    assert outer.rect.size == Vec2(100, 100)


def test_nested_anchor_layouts(ui):
    outer = UIGridLayout(row_count=1, column_count=1)
    inner = UIAnchorLayout(size_hint_min=(100, 100))

    outer.add(inner, 0, 0)
    ui.add(outer)

    ui.execute_layout()

    assert inner.rect.size == Vec2(100, 100)
    assert outer.rect.size == Vec2(100, 100)


def test_update_size_hint_min_on_child_size_change(ui):
    grid = UIGridLayout(row_count=1, column_count=1)
    dummy = UIDummy(size_hint_min=(100, 100), size_hint=(0, 0))

    grid.add(dummy, 0, 0)
    ui.add(grid)

    dummy.size_hint_min = (200, 200)
    ui.execute_layout()

    assert dummy.rect.size == Vec2(200, 200)
    assert grid.rect.size == Vec2(200, 200)


def test_widgets_are_centered(ui):
    # grid elements not centered
    # https://github.com/pythonarcade/arcade/issues/2210
    grid = UIGridLayout(row_count=1, column_count=1, horizontal_spacing=10, vertical_spacing=10)
    ui.add(grid)

    dummy1 = UIDummy(width=100, height=100)
    grid.add(dummy1, 0, 0)

    ui.execute_layout()

    assert dummy1.rect.bottom_left == Vec2(0, 0)


def test_size_hint_none(ui):
    # size changed when sh None
    grid = UIGridLayout(row_count=1, column_count=1, width=150, height=150, size_hint=None)
    ui.add(grid)

    dummy1 = UIDummy(width=100, height=100, size_hint_max=(150, None))
    grid.add(dummy1, 0, 0)

    ui.execute_layout()

    assert dummy1.rect.size == Vec2(100, 100)


def test_minimal_size(ui):
    grid = ui.add(
        UIGridLayout(
            column_count=3,
            row_count=1,
            size_hint=(0, 0),
        )
    )

    grid.add(UIDummy(width=200, height=100), column=0, row=0, column_span=2)
    grid.add(UIDummy(width=100, height=100), column=2, row=0, row_span=1)

    ui.execute_layout()

    assert grid.size == (300, 100)
    assert grid.size_hint_min == (300, 100)


def test_calculate_size_hint_min(ui):
    dummy1 = UIDummy(width=50, height=100)
    dummy2 = UIDummy(width=100, height=100)
    dummy3 = UIDummy(width=100, height=50)
    dummy4 = UIDummy(width=50, height=50)

    subject = UIGridLayout(column_count=2, row_count=2)

    subject.add(dummy1, 0, 0)
    subject.add(dummy2, 0, 1)
    subject.add(dummy3, 1, 0)
    subject.add(dummy4, 1, 1)

    ui.add(subject)
    ui.execute_layout()

    assert subject.size_hint_min == (200, 200)
