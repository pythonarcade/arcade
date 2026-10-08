"""A UIFlatButton's border reaches the edge of the button, with no gap (#2868)."""

import pytest

from arcade.gui import Surface, UIFlatButton

BG = (0, 0, 255, 255)
BORDER = (255, 0, 0, 255)


@pytest.mark.parametrize("border_width", [2, 4])
def test_border_has_no_gap(window, border_width):
    style = UIFlatButton.UIStyle(bg=BG, border=BORDER, border_width=border_width)
    button = UIFlatButton(x=0, y=0, width=100, height=40, style={"normal": style})
    surface = Surface(size=(100, 40))
    with surface.activate():
        button._do_render(surface, force=True)

    # One pixel wide column through the middle of the button, from the left edge
    data = surface.fbo.read(components=4, viewport=(0, 20, 100, 1))
    row = [tuple(data[i : i + 4]) for i in range(0, len(data), 4)]
    assert row[:border_width] == [BORDER] * border_width
    assert row[border_width] == BG
    assert row[-border_width:] == [BORDER] * border_width
    assert row[-border_width - 1] == BG
