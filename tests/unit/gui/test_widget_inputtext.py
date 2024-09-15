from arcade.gui import UIInputText, UIOnChangeEvent


def test_deactivated_by_default(ui):
    # GIVEN
    widget = UIInputText()

    # THEN
    assert widget.active is False


def test_activated_after_click(ui):
    # GIVEN
    widget = UIInputText()
    ui.add(widget)

    # WHEN
    ui.click(*widget.rect.center)

    # THEN
    assert widget.active is True


def test_deactivated_after_off_click(ui):
    # GIVEN
    widget = UIInputText()
    ui.add(widget)
    widget.activate()

    # WHEN
    ui.click(200, 200)

    # THEN
    assert widget.active is False


def test_captures_text_when_active(ui):
    # GIVEN
    widget = UIInputText()
    ui.add(widget)
    widget.activate()

    # WHEN
    ui.type_text("Hello")

    # THEN
    assert widget.text == "Hello"


def test_does_not_capture_text_when_inactive(ui):
    # GIVEN
    widget = UIInputText()
    ui.add(widget)

    # WHEN
    ui.type_text("Hello")

    # THEN
    assert widget.text == ""


def test_dispatches_on_change_event(ui):
    # GIVEN
    widget = UIInputText()
    ui.add(widget)

    recorded = []

    @widget.event("on_change")
    def on_change(event):
        recorded.append(event)

    # WHEN
    widget.activate()
    ui.type_text("Hello")

    # THEN
    assert len(recorded) == 1

    recorded_event = recorded[0]
    assert isinstance(recorded_event, UIOnChangeEvent)
    assert recorded_event.new_value == "Hello"


def test_setting_text_dispatches_on_change_event(ui):
    # GIVEN
    widget = UIInputText()
    ui.add(widget)

    recorded = []

    @widget.event("on_change")
    def on_change(event):
        recorded.append(event)

    # WHEN
    widget.text = "Hello"

    # THEN
    assert len(recorded) == 1

    recorded_event = recorded[0]
    assert isinstance(recorded_event, UIOnChangeEvent)
    assert recorded_event.new_value == "Hello"
