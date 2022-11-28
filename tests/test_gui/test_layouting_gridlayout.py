from arcade.gui import UIDummy
from arcade.gui.widgets import Rect
from arcade.gui.widgets.layout import UIGridLayout


def test_place_widget(window):
    dummy1 = UIDummy(width=100, height=100)
    dummy2 = UIDummy(width=100, height=100)
    dummy3 = UIDummy(width=100, height=100)
    dummy4 = UIDummy(width=100, height=100)

    subject = UIGridLayout(
        column_count=2,
        row_count=2
    )

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


def test_place_widget_with_different_sizes(window):
    dummy1 = UIDummy(width=50, height=100)
    dummy2 = UIDummy(width=100, height=100)
    dummy3 = UIDummy(width=100, height=50)
    dummy4 = UIDummy(width=50, height=50)

    subject = UIGridLayout(
        column_count=2,
        row_count=2
    )

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

    subject = UIGridLayout(
        column_count=1,
        row_count=1
    ).with_padding(left=10, bottom=20)

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


def test_fit_content_by_default(window):
    subject = UIGridLayout(
        column_count=1,
        row_count=1,
    )

    assert subject.size_hint == (0, 0)


def test_growth_child(window):
    dummy1 = UIDummy(width=100, height=100, size_hint=(1, 1))

    subject = UIGridLayout(
        column_count=1,
        row_count=1,
    )

    subject.add(dummy1, 0, 0)

    subject.resize(width=200, height=300)
    subject.do_layout()

    assert dummy1.size == (200, 300)


def test_shrink_child(window):
    dummy1 = UIDummy(width=100, height=100, size_hint=(1, 1))

    subject = UIGridLayout(
        column_count=1,
        row_count=1,
    )

    subject.add(dummy1, 0, 0)

    subject.resize(width=50, height=60)
    subject.do_layout()

    assert dummy1.size == (50, 60)


def test_adjust_child_size_relative(window):
    dummy1 = UIDummy(width=100, height=100, size_hint=(0.5, 0.5))

    subject = UIGridLayout(
        column_count=1,
        row_count=1,
    )

    subject.add(dummy1, 0, 0)

    subject.resize(width=100, height=200)
    subject.do_layout()

    assert dummy1.size == (50, 100)
