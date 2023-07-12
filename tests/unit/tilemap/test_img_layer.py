import arcade


def test_image_layer():
    # Read in the tiled map
    tile_map = arcade.load_tilemap(":fixtures:tilemaps/image_layer.json")

    # --- Platforms ---
    assert "img" in tile_map.sprite_lists
    assert len(tile_map.sprite_lists["img"]) == 1

