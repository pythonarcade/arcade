from pathlib import Path

import pytiled_parser
from pytiled_parser import LayerGroup, OrderedPair, Size, TileLayer
from pytiled_parser.common_types import Color

import arcade
from arcade import TileMap


def test_one():
    tile_map = arcade.load_tilemap(":resources:/tiled_maps/test_map_1.json")

    assert tile_map.width == 10
    assert tile_map.height == 5
    assert len(tile_map.sprite_lists) == 2
    assert tile_map.background_color == Color(0, 160, 229, 255)

    assert "Platforms" in tile_map.sprite_lists
    platforms_list = tile_map.sprite_lists["Platforms"]
    assert len(platforms_list) == 10

    assert "Background" in tile_map.sprite_lists
    background_list = tile_map.sprite_lists["Background"]
    assert len(background_list) == 2

    first_sprite = platforms_list[0]
    assert first_sprite is not None
    assert first_sprite.center_x == 64
    assert first_sprite.center_y == 64
    assert first_sprite.width == 128
    assert first_sprite.height == 128


def test_two():
    tile_map = arcade.load_tilemap(":resources:tiled_maps/test_map_2.json")

    assert tile_map.width == 10
    assert tile_map.height == 5
    assert len(tile_map.sprite_lists) == 3

    assert "Platforms" in tile_map.sprite_lists
    platforms_list = tile_map.sprite_lists["Platforms"]
    assert len(platforms_list) == 10

    first_sprite = platforms_list[0]
    assert first_sprite is not None
    assert first_sprite.center_x == 64
    assert first_sprite.center_y == 64
    assert first_sprite.width == 128
    assert first_sprite.height == 128

    assert "Dirt" in tile_map.sprite_lists
    dirt_list = tile_map.sprite_lists["Dirt"]

    first_sprite = dirt_list[0]
    assert first_sprite is not None
    first_sprite = dirt_list[1]
    assert first_sprite is not None
    first_sprite = dirt_list[2]
    assert first_sprite is not None

    assert "Coins" in tile_map.sprite_lists
    coin_list = tile_map.sprite_lists["Coins"]

    first_sprite = coin_list[0]
    assert first_sprite is not None


def test_three():
    tile_map = arcade.load_tilemap(":resources:tiled_maps/test_map_3.json")
    assert tile_map is not None

    assert "Moving Platforms" in tile_map.sprite_lists
    sprite_list = tile_map.sprite_lists["Moving Platforms"]

    assert sprite_list is not None
    assert len(sprite_list) == 1
    sprite = sprite_list[0]
    assert sprite.properties is not None
    assert "change_x" in sprite.properties
    assert "change_y" in sprite.properties
    assert sprite.properties["change_x"] == 1
    assert sprite.properties["change_y"] == 1


def test_five():
    tile_map = arcade.load_tilemap(":resources:tiled_maps/test_map_5.json")
    assert tile_map is not None

    assert len(tile_map.object_lists) == 1
    assert "object_layer" in tile_map.object_lists


def test_sprite_sheet():
    tile_map = arcade.load_tilemap(":resources:tiled_maps/test_map_6.json")
    assert tile_map is not None

    assert len(tile_map.sprite_lists) == 1
    assert "Tile Layer 1" in tile_map.sprite_lists

    sprite_list = tile_map.sprite_lists["Tile Layer 1"]

    assert sprite_list is not None
    assert len(sprite_list) == 14

    first_sprite = sprite_list[0]
    assert first_sprite is not None
    assert first_sprite.height == 16
    assert first_sprite.width == 16


def test_find_layer_group():
    child_layer = TileLayer(
        name="P1",
        visible=True,
        repeat_x=False,
        repeat_y=False,
        parallax_factor=OrderedPair(1, 1),
        id=0,
        size=Size(10, 5),
        tint_color=None,
        data=[],
    )
    group = LayerGroup(
        name="Platforms",
        opacity=1,
        repeat_x=False,
        repeat_y=False,
        tint_color=None,
        layers=[child_layer],
    )
    tilemap = TileMap(
        tiled_map=pytiled_parser.TiledMap(
            map_file=Path(),
            infinite=False,
            layers=[group],
            map_size=Size(10, 5),
            next_layer_id=None,
            next_object_id=0,
            orientation="orthogonal",
            render_order="right-down",
            tiled_version="1.5.0",
            tile_size=Size(32, 32),
            tilesets={},
            version="1.5",
            background_color=Color(0, 160, 229, 255),
        )
    )

    layer_group = tilemap.get_tilemap_layer("Platforms")
    assert layer_group is layer_group


def test_find_layer_group_child():
    child_layer = TileLayer(
        name="P1",
        visible=True,
        repeat_x=False,
        repeat_y=False,
        parallax_factor=OrderedPair(1, 1),
        id=0,
        size=Size(10, 5),
        tint_color=None,
        data=[],
    )
    group = LayerGroup(
        name="Platforms",
        opacity=1,
        repeat_x=False,
        repeat_y=False,
        tint_color=None,
        layers=[child_layer],
    )
    tilemap = TileMap(
        tiled_map=pytiled_parser.TiledMap(
            map_file=Path(),
            infinite=False,
            layers=[group],
            map_size=Size(10, 5),
            next_layer_id=None,
            next_object_id=0,
            orientation="orthogonal",
            render_order="right-down",
            tiled_version="1.5.0",
            tile_size=Size(32, 32),
            tilesets={},
            version="1.5",
            background_color=Color(0, 160, 229, 255),
        )
    )

    layer = tilemap.get_tilemap_layer("Platforms/P1")
    assert layer is child_layer
