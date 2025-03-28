def test_colors():
    from arcade import color

    names = color.__dict__.keys()
    # number of colors + 1 real import
    assert 1016 + 1 == len(names)
