import pytest
from PIL import Image
import arcade
from arcade.cache import TextureCache

path = ":resources:images/test_textures/test_texture.png"


@pytest.fixture(scope="function")
def texture():
    return arcade.Texture(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))


@pytest.fixture(scope="module")
def file_texture():
    return arcade.load_texture(":resources:images/test_textures/test_texture.png")


@pytest.fixture(scope="function")
def cache():
    return TextureCache()


def test_create(cache):
    assert cache._entries is not None
    assert cache._file_entries is not None
    assert len(cache) == 0


def test_put(cache, texture):
    cache.put(texture)
    assert cache.get(texture.cache_name) == texture
    assert len(cache) == 1
    assert cache.get_all_textures() == set([texture])
    assert len(cache._entries) == 1
    assert len(cache._file_entries) == 0


def test_put_file(cache, file_texture):
    cache.put(file_texture)
    assert cache.get(file_texture.cache_name) == file_texture
    assert cache.get_texture_by_filepath(file_texture.file_path) == file_texture
    assert len(cache._entries) == 1
    assert len(cache._file_entries) == 1


def test_delete(cache, texture):
    cache.put(texture)
    assert len(cache) == 1
    cache.delete(texture)
    assert len(cache) == 0
    # assert cache.get(texture.cache_name) is None


def test_clear(cache, texture):
    cache.put(texture)
    assert len(cache) == 1
    cache.flush()
    assert len(cache) == 0


def test_contains(cache, texture):
    assert texture not in cache
    cache.put(texture)
    assert texture in cache
    cache.delete(texture)


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
    # assert cache[texture.cache_name] is None
