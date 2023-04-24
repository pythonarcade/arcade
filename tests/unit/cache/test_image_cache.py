import pytest
from PIL import Image
from arcade.texture import ImageData
from arcade.cache import ImageDataCache

image_1 = ImageData(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
image_2 = ImageData(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))


@pytest.fixture(scope="function")
def cache():
    return ImageDataCache()


def test_create(cache):
    assert len(cache) == 0
    assert cache._entries_strong is not None
    assert cache._entries_weak is not None


def test_put_strong(cache):
    cache.put("test", image_1, weak=False)
    assert len(cache) == 1
    assert cache.get("test") == image_1
    assert cache["test"] == image_1


def test_put_weak(cache):
    image = ImageData(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
    cache.put("test", image, weak=True)
    assert cache.get("test") == image
    assert cache["test"] == image
    assert len(cache) == 1

    image = None
    assert len(cache) == 0


def test_delete(cache):
    cache.put("test_1", image_1, weak=False)
    cache.put("test_2", image_2, weak=False)
    assert len(cache) == 2

    cache.delete("test_1")
    assert len(cache) == 1
    cache.delete("test_2")
    assert len(cache) == 0

    cache.put("test_1", image_1, weak=False)
    cache.put("test_2", image_2, weak=False)

    del cache["test_1"]
    assert len(cache) == 1
    del cache["test_2"]
    assert len(cache) == 0
