from arcade.texture import (
    Texture,
    ImageData,
    get_default_texture,
    get_default_image,
    default_texture_cache
)


def test_default_image():
    image = get_default_image()
    assert isinstance(image, ImageData)
    assert image.size == (128, 128)

    # Ensure we get cached version
    assert id(get_default_image()) == id(image)
    default_texture_cache.flush()
    assert id(get_default_image()) != id(image)


def test_default_texture():
    texture = get_default_texture()
    assert isinstance(texture, Texture)
    assert texture.size == (128, 128)
    assert texture.image.size == (128, 128)

    # Ensure we get cached version
    assert id(get_default_texture()) == id(texture)
