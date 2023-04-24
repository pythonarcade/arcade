
def test_colors():
    from arcade import color
    names = color.__dict__.keys()
    # number of colors + 1 import
    assert 1013 + 1 == len(names)
