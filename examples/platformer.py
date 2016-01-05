import random
import math
import arcade

SCALE = 0.0015

class PlayerSprite(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.update_count = 0

    def update(self):
        self.update_count += 1

        if self.update_count % 120 == 0:
            self.cur_texture_index += 1
            if self.cur_texture_index >= len(self.textures):
                self.cur_texture_index = 0
            self.texture = self.textures[self.cur_texture_index]

class MyApplication(arcade.ArcadeApplication):
    """ Main application class. """

    def __init__(self):
        pass

    def setup_game(self):
        self.all_sprites_list = arcade.SpriteList()

        x_pos = 0
        pixel_width = 72
        pixel_height = 93
        y_border = 4
        x_border = 0
        scale = 0.004

        image_location_list = []

        for y in range(0, pixel_height * 2, pixel_height + y_border):
            for x in range(0, pixel_width * 7, pixel_width + x_border):
                image_location = (x, y, pixel_width, pixel_height)
                image_location_list.append(image_location)

        texture_info_list = arcade.load_textures("images/p1_spritesheet.png", image_location_list)

        self.player = PlayerSprite()
        for texture_info in texture_info_list:
            texture, width, height = texture_info
            self.player.append_texture(texture)

        self.player.set_texture(0)
        self.player.width = pixel_width * scale
        self.player.height = pixel_height * scale
        self.player.center_x = x_pos
        x_pos += 0.15
        self.all_sprites_list.append(self.player)

    def render(self):
        arcade.start_render()

        self.all_sprites_list.draw()
        arcade.draw_text("Texture: {}".format(self.player.cur_texture_index), 0, -0.3, arcade.color.WHITE)

        arcade.swap_buffers()

    def key_pressed(self, key, x, y):
        if not self.player_sprite.respawning and key == b' ':
            pass

    def special_pressed(self, key, x, y):
        if key == arcade.key.LEFT:
            self.player_sprite.change_angle = 3
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_angle = -3
        elif key == arcade.key.UP:
            self.player_sprite.thrust = .0005
        elif key == arcade.key.DOWN:
            self.player_sprite.thrust = -.0002

    def special_released(self, key, x, y):
        if key == arcade.key.LEFT:
            self.player_sprite.change_angle = 0
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_angle = 0
        elif key == arcade.key.UP:
            self.player_sprite.thrust = 0
        elif key == arcade.key.DOWN:
            self.player_sprite.thrust = 0


    def animate(self):

        self.all_sprites_list.update()
        arcade.redisplay()

    def run(self):

        self.open_window(1400, 1000)
        self.setup_game()

        arcade.run()

app = MyApplication()
app.run()
