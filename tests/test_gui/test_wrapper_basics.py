from arcade.gui.widgets import UIDummy, UIBorder, UIWrapper


def test_wrap_calculates_padding():
    # GIVEN
    child = UIDummy()

    # WHEN
    widget = UIWrapper(child=child, padding=(1, 2, 3, 4))

    # THEN
    assert widget.rect == (-4, -3, 106, 104)
    assert child.rect == (0, 0, 100, 100)
