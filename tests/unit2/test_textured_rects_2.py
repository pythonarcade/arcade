import arcade

SCREEN_TITLE = "Resources"


def test_textured_rects_2(window: arcade.Window):
    """Draw scaled rects"""
    arcade.set_background_color(arcade.color.AMAZON)
    texture = arcade.load_texture(":resources:images/items/coinGold.png")

    def on_draw():
        arcade.start_render()
        x = 50
        y = 50
        scale = 1.0
        # assert arcade.get_pixel(50, 50) == (59, 122, 87)
        arcade.draw_scaled_texture_rectangle(x, y, texture, scale)
        # assert arcade.get_pixel(50, 50) == (255, 204, 0)

    window.on_draw = on_draw
    window.test(10)
