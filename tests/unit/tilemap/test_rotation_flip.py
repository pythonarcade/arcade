import arcade
from arcade.texture import transforms as tt


def _transform(*transforms):
    """Apply vertex order or multiple transforms"""
    t = transforms[0]
    order = t.order
    for transform in transforms[1:]:
        order = transform.transform_vertex_order(order)
    return order


def test_rotation_mirror(window, fixtures):
    # Read in the tiled map
    print(fixtures)
    my_map = arcade.load_tilemap(fixtures.path("rotation.json"))

    assert my_map.tile_width == 128
    assert my_map.tile_height == 128
    assert my_map.width == 11
    assert my_map.height == 10


    # --- Platforms ---
    assert "Blocking Sprites" in my_map.sprite_lists
    wall_list = my_map.sprite_lists["Blocking Sprites"]
    wall = wall_list[0]
    assert wall.position == (64, 64)
    # Default position
    assert wall.texture.image.getpixel((0, 0)) == (255, 0, 0, 255)
    assert wall.texture.image.getpixel((127, 0)) == (0, 255, 0, 255)
    assert wall.texture.image.getpixel((127, 127)) == (255, 0, 255, 255)

    # Horizontal flip
    wall = wall_list[1]
    assert wall.position == (192, 64)
    assert wall.texture._vertex_order == tt.FlipLeftRightTransform.order

    # Transpose and flipped horizontally
    wall = wall_list[2]
    assert wall.position == (448, 64)
    assert wall.texture._vertex_order == tt.FlipLeftRightTransform.transform_vertex_order(tt.TransposeTransform.order)

    # Transposed, flipped vertically and horizontally
    wall = wall_list[3]
    assert wall.position == (576, 64)
    assert wall.texture._vertex_order == _transform(tt.TransposeTransform, tt.FlipLeftRightTransform, tt.FlipTopBottomTransform)

    # Horizontal flip and flipped vertically
    wall = wall_list[4]
    assert wall.position == (832, 64)
    assert wall.texture._vertex_order == _transform(tt.FlipLeftRightTransform, tt.FlipTopBottomTransform)

    # Vertical flip
    wall = wall_list[5]
    assert wall.position == (960, 64)
    assert wall.texture._vertex_order == tt.FlipTopBottomTransform.order

    # Transposed and flipped vertically
    wall = wall_list[6]
    assert wall.position == (1216, 64)
    assert wall.texture._vertex_order == _transform(tt.TransposeTransform, tt.FlipTopBottomTransform)

    # Transposed
    wall = wall_list[7]
    assert wall.position == (1344, 64)
    assert wall.texture._vertex_order == tt.TransposeTransform.order
