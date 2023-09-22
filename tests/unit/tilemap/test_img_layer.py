import arcade


def test_image_layer():
    # Read in the tiled map
    tile_map = arcade.load_tilemap(":fixtures:tilemaps/image_layer.json")

    # --- Platforms ---
    assert "img" in tile_map.sprite_lists
    assert len(tile_map.sprite_lists["img"]) == 1

    image = tile_map.sprite_lists["img"][0]

    assert image.width == 1024
    assert image.height == 600
    assert image.left == 0
    assert image.top == 1920

    assert "img-offset" in tile_map.sprite_lists
    assert len(tile_map.sprite_lists["img-offset"]) == 1
    image = tile_map.sprite_lists["img-offset"][0]
    
    assert image.width == 1024
    assert image.height == 600
    assert image.left == 1280
    assert image.top == 1408


def test_image_layer_with_scaling():
    # Read in the tiled map
    tile_map = arcade.load_tilemap(":fixtures:tilemaps/image_layer.json", 0.5)

    # --- Platforms ---
    assert "img" in tile_map.sprite_lists
    assert len(tile_map.sprite_lists["img"]) == 1
    image = tile_map.sprite_lists["img"][0]

    assert image.width == 512
    assert image.height == 300
    assert image.left == 0
    assert image.top == 960

    assert "img-offset" in tile_map.sprite_lists
    assert len(tile_map.sprite_lists["img-offset"]) == 1
    image = tile_map.sprite_lists["img-offset"][0]
    
    assert image.width == 512
    assert image.height == 300
    assert image.left == 640
    assert image.top == 704