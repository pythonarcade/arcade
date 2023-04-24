from arcade.texture import ImageData
from PIL import Image


def test_create_sha256():
    ImageData.hash_func = "sha256"
    img = Image.new("RGBA", (10, 20), (0, 0, 0, 0))
    data = ImageData(img)
    assert data.size == (10, 20)
    assert data.width == 10
    assert data.height == 20
    assert data.image == img
    assert data.hash == "67042dfda5683aead81b6055d19c4dba238341f9dd82f49c0e7cc0c19c5f10d1"
    assert hash(data) == hash(data.hash)


def test_create_md5():
    ImageData.hash_func = "md5"
    img = Image.new("RGBA", (10, 20), (0, 0, 0, 0))
    data = ImageData(img)
    assert data.size == (10, 20)
    assert data.width == 10
    assert data.height == 20
    assert data.image == img
    assert data.hash == "6b431bf2da7c9312b3e5c21e67f6591b"
    assert hash(data) == hash(data.hash)


def test_create_specify_hash():
    ImageData.hash_func = "sha256"
    img = Image.new("RGBA", (10, 20), (0, 0, 0, 0))
    data = ImageData(img, "test")
    assert data.size == (10, 20)
    assert data.width == 10
    assert data.height == 20
    assert data.image == img
    assert data.hash == "test"
    assert hash(data) == hash(data.hash)


def test_uniqueness():
    data_1 = ImageData(Image.new("RGBA", (10, 20), (0, 0, 0, 0)))
    data_2 = ImageData(Image.new("RGBA", (10, 20), (0, 0, 0, 0)))
    data_3 = ImageData(Image.new("RGBA", (10, 20), (255, 0, 0, 0)))

    assert data_1 == data_2
    assert data_1 != data_3
    assert data_2 != data_3

    assert len({data_1, data_2, data_3}) == 2
    assert len({data_2, data_3}) == 2
    assert len({data_1, data_2}) == 1
