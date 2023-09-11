
def test_key():
    from arcade import key
    names = key.__dict__.keys()
    # temp fix which will be replaced with fuller, more meaningful
    # tests in the coming days. The values are as follows:
    # 214 key constants + from __future__ import annotations
    assert 215 == len(names)
