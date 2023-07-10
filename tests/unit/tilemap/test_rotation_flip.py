import arcade
from arcade.texture import transforms as tt


def _transform(*transforms):
    """Apply vertex order or multiple transforms"""
    t = transforms[0]
    order = t.order
    for transform in transforms[1:]:
        order = transform.transform_vertex_order(order)
    return order


def test_rotation_mirror():
    # Read in the tiled map
    my_map = arcade.load_tilemap(":fixtures:tilemaps/rotation.json")

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


def test_object_rotation_orientation():
    # Read in the tiled map
    my_map = arcade.load_tilemap(":fixtures:tilemaps/rotation.json")

    assert my_map.tile_width == 128
    assert my_map.tile_height == 128
    assert my_map.width == 11
    assert my_map.height == 10
    # --- Object ---
    assert "Objects Sprites" in my_map.sprite_lists
    wall_list = my_map.sprite_lists["Objects Sprites"]
    
    # Check for the direction of rotation
    # not rotated the top is aligned with the grid
    wall = wall_list[16]
    assert wall.properties["name"] == "r0"
    assert (wall.top / 128).is_integer()
    assert not (wall.bottom / 128).is_integer()
    assert (wall.left / 128).is_integer()
    assert (wall.right / 128).is_integer()

    # Turned 90 to the left
    wall = wall_list[17]
    assert wall.properties["name"] == "r1"
    assert (wall.top / 128).is_integer()
    assert (wall.bottom / 128).is_integer()
    assert (wall.left / 128).is_integer()
    assert not (wall.right / 128).is_integer()

    # Turned 180 
    wall = wall_list[18]
    assert wall.properties["name"] == "r2"
    assert not (wall.top / 128).is_integer()
    assert (wall.bottom / 128).is_integer()
    assert (wall.left / 128).is_integer()
    assert (wall.right / 128).is_integer()

    # Turned 270 to the left (90 to the right) 
    wall = wall_list[19]
    assert wall.properties["name"] == "r3"
    assert (wall.top / 128).is_integer()
    assert (wall.bottom / 128).is_integer()
    assert not (wall.left / 128).is_integer()
    assert (wall.right / 128).is_integer()


def test_object_rotation_placement():
    # Read in the tiled map
    my_map = arcade.load_tilemap(":fixtures:tilemaps/rotation.json")

    # --- Object ---
    assert "Objects Sprites" in my_map.sprite_lists
    wall_list = my_map.sprite_lists["Objects Sprites"]

    line = 64+128*2
    wall = wall_list[0]
    assert wall.properties["name"] == "not"
    assert wall.position == (64, line)

    wall = wall_list[1]
    assert wall.properties["name"] == "h"
    assert wall.position == (64+128*1, line)

    wall = wall_list[2]
    assert wall.properties["name"] == "90"
    assert wall.position == (64+128*3, line)

    wall = wall_list[3]
    assert wall.properties["name"] == "h90"
    assert wall.position == (64+128*4, line)

    wall = wall_list[4]
    assert wall.properties["name"] == "180"
    assert wall.position == (64+128*6, line)
    
    wall = wall_list[5]
    assert wall.properties["name"] == "h180"
    assert wall.position == (64+128*7, line)

    wall = wall_list[6]
    assert wall.properties["name"] == "-90"
    assert wall.position == (64+128*9, line)

    wall = wall_list[7]
    assert wall.properties["name"] == "h-90"
    assert wall.position == (64+128*10, line)

    line = 64+128*4
    wall = wall_list[8]
    assert wall.properties["name"] == "v"
    assert wall.position == (64, line)

    wall = wall_list[9]
    assert wall.properties["name"] == "hv"
    assert wall.position == (64+128*1, line)

    wall = wall_list[10]
    assert wall.properties["name"] == "v90"
    assert wall.position == (64+128*3, line)

    wall = wall_list[11]
    assert wall.properties["name"] == "hv90"
    assert wall.position == (64+128*4, line)

    wall = wall_list[12]
    assert wall.properties["name"] == "v180"
    assert wall.position == (64+128*6, line)

    wall = wall_list[13]
    assert wall.properties["name"] == "hv180"
    assert wall.position == (64+128*7, line)

    wall = wall_list[14]
    assert wall.properties["name"] == "v-90"
    assert wall.position == (64+128*9, line)

    wall = wall_list[15]
    assert wall.properties["name"] == "hv-90"
    assert wall.position == (64+128*10, line)