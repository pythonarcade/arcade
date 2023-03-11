from arcade.gui.widgets.slider import UISlider


def test_initial_value_set():
    # GIVEN

    # WHEN
    slider = UISlider(height=30, width=120)

    # THEN
    assert slider.value == 0


def test_change_value_on_drag(uimanager):
    # GIVEN
    slider = UISlider(height=30, width=120)
    uimanager.add(slider)

    assert slider.value == 0

    # WHEN
    cx, cy = slider._cursor_pos()
    uimanager.click_and_hold(cx, cy)
    uimanager.drag(cx + 20, cy)

    # THEN
    assert slider.value == 20
