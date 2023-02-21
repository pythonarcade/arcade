
def test_key():
    from arcade import key
    names = key.__dict__.keys()
    assert 214 == len(names)
