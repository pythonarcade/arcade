from arcade.gui import UIInputText


def test_activates_on_click(ui):
    # GIVEN
    it = UIInputText(height=30, width=120)
    ui.add(it)

    assert it.active is False

    # WHEN
    ui.click(*it.center)

    # THEN
    assert it.active


def test_deactivates_on_click(ui):
    # GIVEN
    it = UIInputText(height=30, width=120)
    ui.add(it)
    it.activate()

    # WHEN
    ui.click(*it.rect.top_left - (1, 0))

    # THEN
    assert it.active is False


def test_changes_state_invalid(ui):
    # GIVEN
    it = UIInputText(height=30, width=120)

    # WHEN
    it.invalid = True

    # THEN
    assert it.get_current_state() == "invalid"
