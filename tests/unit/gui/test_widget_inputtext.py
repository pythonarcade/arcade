from arcade.gui import UIInputText


def test_deactivated_by_default(uimanager):
    # GIVEN
    widget = UIInputText()

    # THEN
    assert widget.active is False


def test_activated_after_click(uimanager):
    # GIVEN
    widget = UIInputText()
    uimanager.add(widget)

    # WHEN
    uimanager.click(*widget.rect.center)

    # THEN
    assert widget.active is True


def test_deactivated_after_off_click(uimanager):
    # GIVEN
    widget = UIInputText()
    uimanager.add(widget)
    widget.activate()

    # WHEN
    uimanager.click(200, 200)

    # THEN
    assert widget.active is False


def test_captures_text_when_active(uimanager):
    # GIVEN
    widget = UIInputText()
    uimanager.add(widget)
    widget.activate()

    # WHEN
    uimanager.type_text("Hello")

    # THEN
    assert widget.text == "Hello"


def test_does_not_capture_text_when_inactive(uimanager):
    # GIVEN
    widget = UIInputText()
    uimanager.add(widget)

    # WHEN
    uimanager.type_text("Hello")

    # THEN
    assert widget.text == ""
