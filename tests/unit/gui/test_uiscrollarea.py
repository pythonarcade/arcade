import pytest

import arcade
from arcade.gui import UIBoxLayout, UIDummy
from arcade.gui.experimental.scroll_area import UIScrollArea


@pytest.fixture
def scroll_setup(ui):
    """A 300x300 scroll area at (0, 0) with 10 rows of 50px height (500px content)."""
    scroll_area = ui.add(UIScrollArea(width=300, height=300))
    box = UIBoxLayout()
    for _ in range(10):
        box.add(UIDummy(width=100, height=50))
    scroll_area.add(box)
    ui.execute_layout()
    return ui, scroll_area, box


def test_canvas_grows_with_content(scroll_setup):
    ui, scroll_area, box = scroll_setup

    # canvas height fits the content, width covers at least the viewport
    assert scroll_area.surface.size == (300, 500)


def test_canvas_covers_at_least_the_viewport(ui):
    scroll_area = ui.add(UIScrollArea(width=300, height=300))
    scroll_area.add(UIDummy(width=100, height=100))

    ui.execute_layout()

    assert scroll_area.surface.size == (300, 300)


def test_surface_uses_window_pixel_ratio(window, ui):
    scroll_area = UIScrollArea()

    assert scroll_area.surface.pixel_ratio == window.get_pixel_ratio()


def test_canvas_size_is_deprecated(ui):
    with pytest.warns(DeprecationWarning):
        UIScrollArea(canvas_size=(100, 100))


def test_scroll_position_preserved_on_content_growth(scroll_setup):
    ui, scroll_area, box = scroll_setup
    scroll_area.scroll_y = -150

    box.add(UIDummy(width=100, height=50))
    ui.execute_layout()

    assert scroll_area.surface.size == (300, 550)
    assert scroll_area.scroll_y == -150


def test_scroll_position_clamped_on_content_shrink(scroll_setup):
    ui, scroll_area, box = scroll_setup
    scroll_area.scroll_y = -200

    # shrink content below the viewport height, scroll range becomes 0
    for child in list(box.children)[:6]:
        box.remove(child)
    ui.execute_layout()

    assert scroll_area.scroll_y == 0


def test_mouse_scroll(scroll_setup):
    ui, scroll_area, box = scroll_setup

    ui.on_mouse_scroll(150, 150, 0, 1)

    assert scroll_area.scroll_y == -scroll_area.scroll_speed


def test_mouse_scroll_is_clamped(scroll_setup):
    ui, scroll_area, box = scroll_setup

    ui.on_mouse_scroll(150, 150, 0, -100)

    # scroll range is content height (300) - canvas height (500)
    assert scroll_area.scroll_y == 0

    ui.on_mouse_scroll(150, 150, 0, 100)
    assert scroll_area.scroll_y == -200


def test_keyboard_scrolling_when_hovered(scroll_setup):
    ui, scroll_area, box = scroll_setup
    ui.move_mouse(150, 150)

    ui.on_key_press(arcade.key.DOWN, 0)
    assert scroll_area.scroll_y == -scroll_area.scroll_speed

    ui.on_key_press(arcade.key.UP, 0)
    assert scroll_area.scroll_y == 0

    ui.on_key_press(arcade.key.PAGEDOWN, 0)
    assert scroll_area.scroll_y == -200  # one page (300) clamped to scroll range

    ui.on_key_press(arcade.key.HOME, 0)
    assert scroll_area.scroll_y == 0

    ui.on_key_press(arcade.key.END, 0)
    assert scroll_area.scroll_y == -200


def test_no_keyboard_scrolling_without_hover(scroll_setup):
    ui, scroll_area, box = scroll_setup
    ui.move_mouse(350, 350)

    ui.on_key_press(arcade.key.DOWN, 0)

    assert scroll_area.scroll_y == 0


def test_no_horizontal_keyboard_scrolling_if_content_fits(scroll_setup):
    ui, scroll_area, box = scroll_setup
    ui.move_mouse(150, 150)

    ui.on_key_press(arcade.key.RIGHT, 0)

    assert scroll_area.scroll_x == 0


def test_scroll_speed_via_constructor(ui):
    scroll_area = UIScrollArea(scroll_speed=42.0, invert_scroll=True)

    assert scroll_area.scroll_speed == 42.0
    assert scroll_area.invert_scroll is True

    # defaults come from the class attributes
    default_area = UIScrollArea()
    assert default_area.scroll_speed == UIScrollArea.scroll_speed
    assert default_area.invert_scroll is UIScrollArea.invert_scroll
