from arcade.texture import ImageData
from PIL import Image


def test_create_sha256():
    ImageData.hash_func = "sha256"
    img = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    data = ImageData(img)
    assert data.image == img
    assert data.hash == "7a12e561363385e9dfeeab326368731c030ed4b374e7f5897ac819159d2884c5"


def test_create_md5():
    ImageData.hash_func = "md5"
    img = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    data = ImageData(img)
    assert data.image == img
    assert data.hash == "a75d7d422fd00bf31208b013e74d8394"


def test_create_specify_hash():
    ImageData.hash_func = "sha256"
    img = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    data = ImageData(img, "test")
    assert data.image == img
    assert data.hash == "test"
