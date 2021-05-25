from pathlib import Path
import arcade

TILE_SCALING = 0.5


def test_show_tilemap(window: arcade.Window):
    my_map = arcade.tilemap.read_map(Path(__file__).parent.resolve() / "../tiled_maps/animation.json")
    wall_list = arcade.tilemap.process_layer(my_map, 'Blocking Sprites', TILE_SCALING)

    if my_map.background_color:
        arcade.set_background_color(my_map.background_color)

    def on_update(delta_time):
        wall_list.update_animation(delta_time)

    def on_draw():
        arcade.start_render()
        wall_list.draw()

    window.on_draw = on_draw
    window.on_update = on_update

    window.test(10)
