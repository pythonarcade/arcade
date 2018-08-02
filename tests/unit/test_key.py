def test_key(mock_window):
    from arcade import key
    names = key.__dict__.keys()
    assert 206 == len(names)
