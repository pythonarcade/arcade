import pytest

from arcade.gui import UIDummy


@pytest.mark.parametrize(
    "attribute, modification",
    [
        ("rect", lambda w: w.move(1, 1)),
        ("visible", lambda w: setattr(w, "visible", False)),
        ("children", lambda w: w.add(UIDummy())),
        ("border", lambda w: w.with_border()),
        ("padding", lambda w: w.with_padding(all=5)),
    ],
)
def test_widget_triggers_render_when_changed(window, attribute, modification):
    # GIVEN
    widget = UIDummy()
    widget._requires_render = False

    # WHEN
    modification(widget)

    # THEN
    assert widget._requires_render
