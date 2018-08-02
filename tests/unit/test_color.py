def test_colors(mock_window):
    from arcade import color
    names = color.__dict__.keys()
    assert 1012 == len(names)
