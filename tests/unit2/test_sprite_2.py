import arcade

CHARACTER_SCALING = 1.0


def test_sprite_2(window):
    arcade.set_background_color(arcade.color.AMAZON)

    sprite = arcade.Sprite(":resources:images/items/coinGold.png", CHARACTER_SCALING)
    sprite.center_x = 50
    sprite.center_y = 50

    sprite_list = arcade.SpriteList()
    sprite_list.append(sprite)

    def on_draw():
        arcade.start_render()
        assert arcade.get_pixel(50, 50) == (59, 122, 87)
        sprite.draw()
        assert arcade.get_pixel(50, 50) == (255, 204, 0)

    window.on_draw = on_draw
    window.test(2)
