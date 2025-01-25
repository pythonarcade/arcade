from arcade import LBWH
from arcade.gui import UIBoxLayout, UIDummy
from pyglet.math import Vec2


def test_uiboxlayout_bars_with_size_hint(window):
    """
    Create a top and bottom bar with fix size, and a growing center area.
    """
    box = UIBoxLayout(size_hint=(1, 1))

    top_bar = UIDummy(height=50, size_hint=(1, 0), size_hint_min=(None, 50))
    box.add(top_bar)

    center_area = UIDummy(size_hint=(1, 1))
    box.add(center_area)

    bottom_bar = UIDummy(height=100, size_hint=(1, 0), size_hint_min=(None, 100))
    box.add(bottom_bar)

    box.rect = LBWH(0, 0, 800, 600)
    box._do_layout()
    box._do_layout()

    assert box.size == Vec2(800, 600)
    assert top_bar.rect == LBWH(0, 550, 800, 50)
    assert center_area.rect == LBWH(0, 100, 800, 450)
    assert bottom_bar.rect == LBWH(0, 0, 800, 100)


def test_uiboxlayout_vertical_bars_with_size_hint(window):
    """
    Create a top and bottom bar with fix size, and a growing center area.
    """
    box = UIBoxLayout(size_hint=(1, 1), vertical=False)

    left_bar = UIDummy(size_hint=(0, 1), size_hint_min=(50, None))
    box.add(left_bar)

    center_area = UIDummy(size_hint=(1, 1))
    box.add(center_area)

    right_bar = UIDummy(size_hint=(0, 1), size_hint_min=(100, None))
    box.add(right_bar)

    box.rect = LBWH(0, 0, 800, 600)
    box._do_layout()
    # box._do_layout()

    assert box.size == Vec2(800, 600)
    assert left_bar.rect == LBWH(0, 0, 50, 600)
    assert center_area.rect == LBWH(50, 0, 650, 600)
    assert right_bar.rect == LBWH(700, 0, 100, 600)
