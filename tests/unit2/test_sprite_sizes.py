import os
import arcade

SIZE = 50
SPACING = SIZE * 2
ROW_SPACING = 100


def test_sprite_sizes(window: arcade.Window):
    arcade.set_background_color(arcade.color.BLACK)

    character_list = arcade.SpriteList()

    for i in range(7):
        my_width = SIZE
        my_height = SIZE + i * 3
        my_color = (i * 40, 0, 255)
        center_x = SPACING + (i * SPACING)
        center_y = ROW_SPACING
        character_sprite = arcade.SpriteSolidColor(my_width, my_height, my_color)
        character_sprite.center_x = center_x
        character_sprite.center_y = center_y
        character_list.append(character_sprite)

    for i in range(7):
        my_width = SIZE + i * 3
        my_height = SIZE
        my_color = (0, i * 40, 255)
        center_x = SPACING + (i * SPACING)
        center_y = ROW_SPACING * 2
        character_sprite = arcade.SpriteSolidColor(my_width, my_height, my_color)
        character_sprite.center_x = center_x
        character_sprite.center_y = center_y
        character_list.append(character_sprite)

    def on_draw():
        arcade.start_render()
        character_list.draw()

        for i in range(7):
            my_width = SIZE
            my_height = SIZE + i * 3
            my_color = (i * 40, 0, 255)
            center_x = SPACING + (i * SPACING)
            center_y = ROW_SPACING

            # Sample bottom
            pixel_color = arcade.get_pixel(center_x, center_y - (my_height // 2 - 4))
            assert pixel_color == my_color

            # Sample top
            pixel_color = arcade.get_pixel(center_x, center_y + (my_height // 2 - 4))
            assert pixel_color == my_color

            # Sample right
            print(center_x + (my_width // 2 - 1), center_y)
            pixel_color = arcade.get_pixel(center_x + (my_width // 2 - 4), center_y)
            assert pixel_color == my_color

        for i in range(7):
            my_width = SIZE + i * 3
            my_height = SIZE
            my_color = (0, i * 40, 255)
            center_x = SPACING + (i * SPACING)
            center_y = ROW_SPACING * 2

            # Sample bottom
            pixel_color = arcade.get_pixel(center_x, center_y - (my_height // 2 - 4))
            assert pixel_color == my_color

            # Sample top
            pixel_color = arcade.get_pixel(center_x, center_y + (my_height // 2 - 4))
            assert pixel_color == my_color

    window.on_draw = on_draw
    window.test()
