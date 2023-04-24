import pytest
import arcade.cache
from arcade import Texture, load_texture
from arcade.cache import HitBoxCache
from arcade import hitbox


@pytest.fixture(scope="function")
def cache():
    """Create a new cache for each test"""
    return HitBoxCache()


def test_create(cache):
    assert len(cache) == 0
    print(repr(cache))
    assert repr(cache) == "HitBoxCache(entries=0)"


def test_put_get(cache):
    cache.put("a|simple", [1, 2, 3, 4])
    cache.put("b|simple", [5, 6, 7, 8])
    cache.put("c|simple", [9, 10, 11, 12])
    assert cache.get("a|simple") == (1, 2, 3, 4)
    assert cache.get("b|simple") == (5, 6, 7, 8)
    assert cache.get("c|simple") == (9, 10, 11, 12)


def test_put_get_different_algorithms(cache):
    cache.put("a|simple", [1, 2, 3, 4])
    cache.put("a|detailed", [5, 6, 7, 8])
    assert cache.get("a|simple") == (1, 2, 3, 4)
    assert cache.get("a|detailed") == (5, 6, 7, 8)


def test_iter(cache):
    cache.put("a|simple", [1, 2, 3, 4])
    cache.put("b|simple", [5, 6, 7, 8])
    cache.put("c|simple", [9, 10, 11, 12])
    assert list(cache) == ["a|simple", "b|simple", "c|simple"]


def test_put_illegal_points(cache):
    # 0 points is allowed for empty textures
    cache.put("a|simple", [])

    # 3 points should work
    cache.put("b|simple", [1, 2, 3])

    # 2 points is not enough to create a polygon
    with pytest.raises(ValueError):
        cache.put("c|simple", [1, 2])


@pytest.mark.parametrize("file_type", ["json", "json.gz"])
def test_save_load(tmp_path, cache, file_type):
    cache.put("a|simple", [1, 2, 3, 4])
    cache.put("b|simple", [5, 6, 7, 8])
    cache.put("b|detailed", [9, 10, 11, 12])

    cache.save(tmp_path / file_type)
    cache.clear()
    assert len(cache) == 0

    cache.load(tmp_path / file_type)
    assert cache.get("a|simple") == (1, 2, 3, 4)
    assert cache.get("b|simple") == (5, 6, 7, 8)
    assert cache.get("b|detailed") == (9, 10, 11, 12)


def test_load_texture():
    arcade.cache.hit_box_cache = HitBoxCache()
    file = ":resources:images/space_shooter/playerShip1_orange.png"

    # We don't cache hit boxes with no algo
    texture = load_texture(file, hit_box_algorithm=hitbox.algo_bounding_box)
    assert arcade.cache.hit_box_cache.get(texture.cache_name) is None
    assert len(arcade.cache.hit_box_cache) == 0

    # We cache hit boxes with an algo
    texture_1 = load_texture(file, hit_box_algorithm=hitbox.algo_simple)
    texture_2 = load_texture(file, hit_box_algorithm=hitbox.algo_detailed)
    assert len(arcade.cache.texture_cache) == 3
    assert len(arcade.cache.hit_box_cache) == 2

    points_1 = arcade.cache.hit_box_cache.get(texture_1)
    points_2 = arcade.cache.hit_box_cache.get(texture_2)
    assert points_1 is not None
    assert points_2 is not None
    assert points_1 != points_2
