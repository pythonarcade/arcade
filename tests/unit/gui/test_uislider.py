from arcade.gui.widgets.slider import UISlider


def test_initial_value_set():
    # GIVEN

    # WHEN
    slider = UISlider(height=30, width=120)

    # THEN
    assert slider.value == 0


def test_change_value_on_drag(ui):
    # GIVEN
    slider = UISlider(height=30, width=120)
    ui.add(slider)

    assert slider.value == 0

    # WHEN
    cx, cy = slider._thumb_x, slider.rect.y
    ui.click_and_hold(cx, cy)
    ui.drag(cx + 20, cy)

    # THEN
    assert slider.value == 20


def test_disable_slider(ui):
    # GIVEN
    slider = UISlider(height=30, width=120)
    ui.add(slider)
    slider.disabled = True

    # WHEN
    cx, cy = slider._thumb_x, slider.rect.y
    ui.click_and_hold(cx, cy)
    ui.drag(cx + 20, cy)

    # THEN
    assert slider.value == 0
