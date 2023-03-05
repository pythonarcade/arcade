from pathlib import Path

import arcade

TILE_SCALING = 0.5


def test_show_tilemap(window: arcade.Window):
    my_map = arcade.load_tilemap(
        Path(__file__).parent.resolve() / "../tiled_maps/animation.json",
        scaling=TILE_SCALING,
    )

    if my_map.background_color:
        window.background_color = my_map.background_color

    def on_update(delta_time):
        my_map.sprite_lists["Blocking Sprites"].update_animation(delta_time)

    def on_draw():
        arcade.start_render()
        my_map.sprite_lists["Blocking Sprites"].draw()

    window.on_draw = on_draw
    window.on_update = on_update

    window.test(10)
