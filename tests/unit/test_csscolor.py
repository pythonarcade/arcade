def test_csscolors(mock_window):
    from arcade import csscolor
    names = csscolor.__dict__.keys()
    assert 156 == len(names)
