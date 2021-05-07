"""
Tests for textures.
"""
import arcade


def test_textured_rects(window: arcade.Window):
    arcade.set_background_color(arcade.color.AMAZON)
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
