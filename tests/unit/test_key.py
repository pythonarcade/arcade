
def test_key():
    from arcade import key
    names = [
        k for k in key.__dict__.keys()
        if not k.startswith("__") and k.isupper()
    ]
    assert 205 == len(names)
