from arcade.gui.experimental import UIPasswordInput
from arcade.gui.experimental.restricted_input import UIRestrictedInput, UIIntInput, UIRegexInput


def test_restricted_input_ignore_invalid_input(ui):
    class FailingInput(UIRestrictedInput):
        def validate(self, text) -> bool:
            return text == ""

    fi = ui.add(FailingInput())

    # WHEN
    ui.click(fi.center_x, fi.center_y)
    for l in "abcdef-.,1234567890":
        ui.type_text(l)

    assert fi.text == ""


def test_int_input_accepts_only_digits(ui):
    fi = ui.add(UIIntInput())

    # WHEN
    ui.click(fi.center_x, fi.center_y)
    for l in "abcdef-.,1234567890":
        ui.type_text(l)

    assert fi.text == "1234567890"


def test_float_input_accepts_only_float(ui):
    fi = ui.add(UIIntInput())

    # WHEN
    ui.click(fi.center_x, fi.center_y)
    for l in "abcdef-.,1234567890":
        ui.type_text(l)

    assert fi.text == "1234567890"


def test_regex_input_accepts_only_matching_patterns(ui):
    fi = ui.add(UIRegexInput(pattern="^[0-9]+$"))

    # WHEN
    ui.click(fi.center_x, fi.center_y)
    for l in "abcdef-.,1234567890":
        ui.type_text(l)

    assert fi.text == "1234567890"

