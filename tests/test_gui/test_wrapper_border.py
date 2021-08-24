from arcade.gui.widgets import UIDummy, UIBorder

def test_wrap_with_default_border():
    # GIVEN
    widget = UIDummy()

    # WHEN
    with_border = widget.with_border()

    # THEN
    assert isinstance(with_border, UIBorder)
    assert with_border.rect == (-2, -2, 104, 104)


def test_wrap_with_extra_wide_border():
    # GIVEN
    border_width = 10
    widget = UIDummy()

    # WHEN
    with_border = widget.with_border(width=border_width)

    # THEN
    assert isinstance(with_border, UIBorder)
    assert with_border.rect == (-border_width, -border_width, 100 + 2 * border_width, 100 + 2 * border_width)
