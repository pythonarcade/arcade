from arcade.gui import UIAnchorLayout
from arcade.gui.widgets.dropdown import UIDropdown

from . import record_ui_events


def test_dropdown_initial_value(ui):
    dropdown = UIDropdown(default="Apple", options=["Apple", "Banana", "Cherry"])
    ui.add(UIAnchorLayout()).add(dropdown, anchor_x="center", anchor_y="center")
    ui.execute_layout()

    assert dropdown.value == "Apple"


def test_dropdown_no_default_value(ui):
    dropdown = UIDropdown(options=["Apple", "Banana", "Cherry"])
    ui.add(UIAnchorLayout()).add(dropdown, anchor_x="center", anchor_y="center")
    ui.execute_layout()

    assert dropdown.value is None


def test_dropdown_select_option_via_click(ui):
    dropdown = UIDropdown(
        default="Apple", options=["Apple", "Banana", "Cherry"], width=200, height=30
    )
    anchor = ui.add(UIAnchorLayout())
    anchor.add(dropdown, anchor_x="center", anchor_y="center")
    ui.execute_layout()

    # Click the dropdown button to open the overlay
    cx, cy = dropdown.rect.center
    ui.click(cx, cy)
    ui.execute_layout()

    # The overlay should now be visible — click the second option ("Banana")
    # Options are stacked below the button, each with height=30
    # First option starts at dropdown.bottom - 2, second option is 30px below that
    option_x = dropdown.left + dropdown.width / 2
    option_y = dropdown.bottom - 2 - 15  # center of first option
    second_option_y = option_y - 30  # center of second option
    ui.click(option_x, second_option_y)

    assert dropdown.value == "Banana"


def test_dropdown_dispatches_on_change_event(ui):
    dropdown = UIDropdown(
        default="Apple", options=["Apple", "Banana", "Cherry"], width=200, height=30
    )
    anchor = ui.add(UIAnchorLayout())
    anchor.add(dropdown, anchor_x="center", anchor_y="center")
    ui.execute_layout()

    with record_ui_events(dropdown, "on_change") as events:
        # Open and click first option (same as current — "Apple")
        cx, cy = dropdown.rect.center
        ui.click(cx, cy)
        ui.execute_layout()

        # Click "Banana" (second option)
        option_x = dropdown.left + dropdown.width / 2
        second_option_y = dropdown.bottom - 2 - 15 - 30
        ui.click(option_x, second_option_y)

    assert len(events) == 1
    assert events[0].old_value == "Apple"
    assert events[0].new_value == "Banana"


def test_dropdown_closes_on_click_outside(ui):
    dropdown = UIDropdown(
        default="Apple", options=["Apple", "Banana", "Cherry"], width=200, height=30
    )
    anchor = ui.add(UIAnchorLayout())
    anchor.add(dropdown, anchor_x="center", anchor_y="center")
    ui.execute_layout()

    # Open the dropdown
    cx, cy = dropdown.rect.center
    ui.click(cx, cy)
    ui.execute_layout()

    # Overlay should be shown (added to manager)
    assert dropdown._overlay.parent is not None

    # Click far outside
    ui.click(10, 10)

    # Overlay should be hidden (removed from manager)
    assert dropdown._overlay.parent is None


def test_dropdown_overlay_height_capped_at_max_height(ui):
    options = [f"Option {i}" for i in range(20)]
    dropdown = UIDropdown(options=options, width=200, height=30, max_height=150)
    anchor = ui.add(UIAnchorLayout())
    anchor.add(dropdown, anchor_x="center", anchor_y="center")
    ui.execute_layout()

    # Total options height would be 20 * 30 = 600, but should be capped at 150
    # Open the dropdown to trigger overlay layout
    cx, cy = dropdown.rect.center
    ui.click(cx, cy)
    ui.execute_layout()

    assert dropdown._overlay.height <= 150


def test_dropdown_scroll_changes_visible_options(ui):
    options = [f"Option {i}" for i in range(20)]
    dropdown = UIDropdown(options=options, width=200, height=30, max_height=150)
    anchor = ui.add(UIAnchorLayout())
    anchor.add(dropdown, anchor_x="center", anchor_y="center")
    ui.execute_layout()

    # Open the dropdown
    cx, cy = dropdown.rect.center
    ui.click(cx, cy)
    ui.execute_layout()

    scroll_area = dropdown._overlay._scroll_area
    initial_scroll = scroll_area.scroll_y

    # Scroll within the overlay
    overlay_cx, overlay_cy = dropdown._overlay.rect.center
    ui.on_mouse_scroll(overlay_cx, overlay_cy, 0, 5)

    assert scroll_area.scroll_y != initial_scroll


def test_dropdown_with_scroll_bar(ui):
    options = [f"Option {i}" for i in range(20)]
    dropdown = UIDropdown(options=options, width=200, height=30, show_scroll_bar=True)
    anchor = ui.add(UIAnchorLayout())
    anchor.add(dropdown, anchor_x="center", anchor_y="center")
    ui.execute_layout()

    assert dropdown._overlay._show_scroll_bar is True


def test_dropdown_without_scroll_bar(ui):
    options = [f"Option {i}" for i in range(20)]
    dropdown = UIDropdown(options=options, width=200, height=30, show_scroll_bar=False)
    anchor = ui.add(UIAnchorLayout())
    anchor.add(dropdown, anchor_x="center", anchor_y="center")
    ui.execute_layout()

    assert dropdown._overlay._show_scroll_bar is False


def test_dropdown_value_setter_updates_button_text(ui):
    dropdown = UIDropdown(
        default="Apple", options=["Apple", "Banana", "Cherry"], width=200, height=30
    )
    anchor = ui.add(UIAnchorLayout())
    anchor.add(dropdown, anchor_x="center", anchor_y="center")
    ui.execute_layout()

    dropdown.value = "Cherry"

    assert dropdown.value == "Cherry"
    assert dropdown._default_button.text == "Cherry"


def test_dropdown_few_options_no_scrolling(ui):
    dropdown = UIDropdown(options=["Apple", "Banana", "Cherry"], width=200, height=30, max_height=200)
    anchor = ui.add(UIAnchorLayout())
    anchor.add(dropdown, anchor_x="center", anchor_y="center")
    ui.execute_layout()

    # Open the dropdown
    cx, cy = dropdown.rect.center
    ui.click(cx, cy)
    ui.execute_layout()

    # Total height is 3 * 30 = 90, well under max_height=200
    assert dropdown._overlay.height == 90

    # Scrolling should have no effect (content fits)
    scroll_area = dropdown._overlay._scroll_area
    overlay_cx, overlay_cy = dropdown._overlay.rect.center
    ui.on_mouse_scroll(overlay_cx, overlay_cy, 0, 5)
    assert scroll_area.scroll_y == 0


def test_dropdown_with_divider(ui):
    options = ["Apple", UIDropdown.DIVIDER, "Banana", "Cherry"]
    dropdown = UIDropdown(default="Apple", options=options, width=200, height=30)
    anchor = ui.add(UIAnchorLayout())
    anchor.add(dropdown, anchor_x="center", anchor_y="center")
    ui.execute_layout()

    # Should not crash; divider is a 2px separator
    assert dropdown.value == "Apple"
    # Options layout should have 4 children (3 buttons + 1 divider widget)
    assert len(dropdown._overlay._options_layout.children) == 4
