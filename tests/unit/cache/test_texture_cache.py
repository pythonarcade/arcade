import pytest
from PIL import Image
import arcade
from arcade.cache import texture_cache
from arcade.cache import TextureCache

path = ":resources:images/test_textures/test_texture.png"


@pytest.fixture(scope="function")
def texture():
    return arcade.Texture(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))


@pytest.fixture(scope="function")
def cache():
    return TextureCache()


def test_create(cache):
    assert cache._strong_entries is not None
    assert cache._weak_entires is not None
    assert cache._strong_file_entries is not None
    assert cache._weak_file_entries is not None
    assert len(cache) == 0


def put_strong(cache, texture):
    cache.put(texture, strong=True)
    assert cache.get(texture.cache_name) == texture


def test_put_weak():
    cache = TextureCache()
    texture = arcade.Texture(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
    cache.put(texture, strong=False)
    cache_name = texture.cache_name
    texture = None
    assert cache.get(cache_name) is None


def test_put_file_strong(cache, texture):
    cache.put(texture, file_path=path, strong=True)
    assert cache.get(texture.cache_name) == texture
    assert cache.get_file(path) == texture


def test_put_file_weak(cache: TextureCache):
    cache = TextureCache()
    texture = arcade.Texture(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
    cache.put(texture, strong=False)
    cache_name = texture.cache_name
    texture = None
    assert cache.get(cache_name) is None
    assert cache.get_file(path) is None


def test_delete(cache, texture):
    cache.put(texture)
    assert len(cache) == 1
    cache.delete(texture)
    assert len(cache) == 0
    assert cache.get(texture.cache_name) is None


def test_clear(cache, texture):
    cache.put(texture)
    assert len(cache) == 1
    cache.clear()
    assert len(cache) == 0

    cache.put(texture, strong=False)
    assert len(cache) == 1
    cache.clear()
    assert len(cache) == 0

    cache.put(texture, file_path=path, strong=True)
    assert len(cache) == 1
    cache.clear()
    assert len(cache) == 0
    assert cache.get(texture.cache_name) is None

    cache.put(texture, file_path=path, strong=False)
    assert len(cache) == 1
    cache.clear()
    assert len(cache) == 0
    assert cache.get(texture.cache_name) is None


def test_contains(cache, texture):
    cache.put(texture)
    assert texture in cache
    cache.delete(texture)
    assert texture not in cache


def test_iter(cache, texture):
    cache.put(texture)
    assert texture in list(cache)
    cache.delete(texture)
    assert texture not in list(cache)


def test_get_set(cache, texture):
    cache.put(texture)
    assert cache[texture.cache_name] == texture
    cache[texture.cache_name] = texture
    assert cache[texture.cache_name] == texture
    del cache[texture.cache_name]
    assert cache[texture.cache_name] is None
