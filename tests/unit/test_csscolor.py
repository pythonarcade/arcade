
def test_csscolors():
    from arcade import csscolor
    names = csscolor.__dict__.keys()
    assert 156 == len(names)
