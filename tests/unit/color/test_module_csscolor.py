
def test_csscolors():
    from arcade import csscolor
    names = csscolor.__dict__.keys()
    # number of colors + 1 import + 1 annotations
    assert 156 + 1 + 1 == len(names)
