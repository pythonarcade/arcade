import os
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SIZE = 50
SPACING = SIZE * 2
ROW_SPACING = 100

class MyTestWindow(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.BLACK)

        self.frame_counter = 0

        self.character_list = arcade.SpriteList()

        for i in range(7):
            my_width = SIZE
            my_height = SIZE + i * 3
            my_color = (i * 40, 0, 255)
            center_x = SPACING + (i * SPACING)
            center_y = ROW_SPACING
            self.character_sprite = arcade.SpriteSolidColor(my_width, my_height, my_color)
            self.character_sprite.center_x = center_x
            self.character_sprite.center_y = center_y
            self.character_list.append(self.character_sprite)

        for i in range(7):
            my_width = SIZE + i * 3
            my_height = SIZE
            my_color = (0, i * 40, 255)
            center_x = SPACING + (i * SPACING)
            center_y = ROW_SPACING * 2
            self.character_sprite = arcade.SpriteSolidColor(my_width, my_height, my_color)
            self.character_sprite.center_x = center_x
            self.character_sprite.center_y = center_y
            self.character_list.append(self.character_sprite)


    def on_draw(self):
        try:
            arcade.start_render()
            self.character_list.draw()

            for i in range(7):
                my_width = SIZE
                my_height = SIZE + i * 3
                my_color = (i * 40, 0, 255)
                center_x = SPACING + (i * SPACING)
                center_y = ROW_SPACING

                # Sample bottom
                pixel_color = arcade.get_pixel(center_x, center_y - (my_height / 2 - 4))
                assert pixel_color == my_color

                # Sample top
                pixel_color = arcade.get_pixel(center_x, center_y + (my_height / 2 - 4))
                assert pixel_color == my_color

                # Sample right
                pixel_color = arcade.get_pixel(center_x + (my_width / 2 - 1), center_y)
                assert pixel_color == my_color

            for i in range(7):
                my_width = SIZE + i * 3
                my_height = SIZE
                my_color = (0, i * 40, 255)
                center_x = SPACING + (i * SPACING)
                center_y = ROW_SPACING * 2

                # Sample bottom
                pixel_color = arcade.get_pixel(center_x, center_y - (my_height / 2 - 1))
                assert pixel_color == my_color

                # Sample top
                pixel_color = arcade.get_pixel(center_x, center_y + (my_height / 2 - 4))
                assert pixel_color == my_color

        except Exception as e:
            assert e is None

def test_sprite():
    window = MyTestWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Test Sprite Sizes")
    window.test()
    window.close()
    arcade.cleanup_texture_cache()
    # arcade.run()