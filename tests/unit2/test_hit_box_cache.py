import arcade
from arcade.cache.hit_box import HitBoxCache


def test_1():
    cache = HitBoxCache()
    assert cache.get("moo") == None

    cache.put("a", [1, 2, 3, 4])
    cache.put("b", [5, 6, 7, 8])
    cache.put("c", [9, 10, 11, 12])
    assert cache.get("a") == [1, 2, 3, 4]
    assert cache.get("b") == [5, 6, 7, 8]
    assert cache.get("c") == [9, 10, 11, 12]
