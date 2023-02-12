import arcade
from arcade import hitbox
from PIL import Image


def test_create():
    texture = arcade.Texture(Image.new("RGBA", (10, 10)))
    assert texture.width == 10
    assert texture.height == 10
    assert texture.file_name is None
    assert texture.image_data.hash == "7a12e561363385e9dfeeab326368731c030ed4b374e7f5897ac819159d2884c5"
    assert texture.cache_name == f"{texture.image_data.hash}|{texture._vertex_order}|{texture.hit_box_algorithm}"


def test_create_override_name():
    texture = arcade.Texture(Image.new("RGBA", (10, 10)), name="test")
    assert texture.cache_name == f"test|{texture._vertex_order}|{texture.hit_box_algorithm}"


def test_hitbox_algo_selection():
    image = Image.new("RGBA", (10, 10), color=(255, 255, 255, 255))

    # Default algorithm
    texture = arcade.Texture(image)
    assert texture.hit_box_algorithm is hitbox.default_algorithm.name

    # Simple algorithm
    texture = arcade.Texture(image, hit_box_algorithm="simple")
    assert texture.hit_box_algorithm == "simple"

    # Detailed algorithm
    texture = arcade.Texture(image, hit_box_algorithm="detailed")
    assert texture.hit_box_algorithm == "detailed"

    # Legacy boundary algorithm
    texture = arcade.Texture(image, hit_box_algorithm=None)
    assert texture.hit_box_algorithm == "bounding_box"


def test_rotate():
    texture = arcade.Texture(Image.new("RGBA", (10, 10)))
    texture_rot90 = texture.rotate_90()

    assert texture._vertex_order != texture_rot90._vertex_order
    assert texture.cache_name != texture_rot90.cache_name
    assert texture.image_data == texture_rot90.image_data
