"""
Tests for textures.
"""
import arcade


def test_textured_rects(window: arcade.Window):
    window.background_color = arcade.color.AMAZON
    texture = arcade.load_texture(":resources:images/space_shooter/playerShip1_orange.png")

    def on_draw():
        arcade.start_render()
        scale = .6
        arcade.draw_texture_rectangle(
            540, 120,
            texture.image.width * scale,
            texture.image.height * scale,
            texture, angle=45,
        )
        arcade.draw_lrwh_rectangle_textured(10, 400, 64, 64, texture)

        for i in range(15):
            arcade.draw_scaled_texture_rectangle(
                i * 50 + 20, 220,
                texture,
                scale,
                angle=45, alpha=i * 15,
            )

    window.on_draw = on_draw
    window.test()


def test_textured_rects_2(window: arcade.Window):
    """Draw scaled rects"""
    window.background_color = arcade.color.AMAZON
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
