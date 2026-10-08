"""Tile map layers get a spatial hash by default (#2663)."""

import pytest

import arcade

MAP = ":resources:tiled_maps/map2_level_1.json"


def test_layers_have_spatial_hash_by_default(window):
    tile_map = arcade.load_tilemap(MAP)
    assert tile_map.sprite_lists
    for sprite_list in tile_map.sprite_lists.values():
        assert sprite_list.spatial_hash is not None


def test_turn_off_for_one_layer(window):
    tile_map = arcade.load_tilemap(MAP, layer_options={"Platforms": {"use_spatial_hash": False}})
    assert tile_map.sprite_lists["Platforms"].spatial_hash is None
    assert tile_map.sprite_lists["Coins"].spatial_hash is not None


def test_turn_off_for_whole_map(window):
    tile_map = arcade.load_tilemap(MAP, use_spatial_hash=False)
    for sprite_list in tile_map.sprite_lists.values():
        assert sprite_list.spatial_hash is None


def test_unknown_layer_option_warns(window):
    with pytest.warns(UserWarning, match="use_spatial_hashing"):
        tile_map = arcade.load_tilemap(
            MAP, layer_options={"Platforms": {"use_spatial_hashing": False}}
        )
    # The misspelled option has no effect
    assert tile_map.sprite_lists["Platforms"].spatial_hash is not None


def test_known_layer_options_dont_warn(window, recwarn):
    arcade.load_tilemap(
        MAP, layer_options={"Platforms": {"use_spatial_hash": True, "scaling": 2.0}}
    )
    assert not [w for w in recwarn if "layer_options" in str(w.message)]
