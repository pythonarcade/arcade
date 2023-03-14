
def test_colors():
    from arcade import color
    names = color.__dict__.keys()
    assert 1013 == len(names)
