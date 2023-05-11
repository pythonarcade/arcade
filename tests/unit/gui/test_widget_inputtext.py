from arcade.gui import UIInputText


def test_uilabel_support_multiline(uimanager):
    # WHEN
    widget = UIInputText()

    # THEN
    assert widget is not None
