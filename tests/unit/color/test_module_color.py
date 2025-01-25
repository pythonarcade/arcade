
def test_colors():
    from arcade import color
    names = color.__dict__.keys()
    # number of colors + 1 real import + 1 annotations
    assert 1016 + 1 + 1 == len(names)
