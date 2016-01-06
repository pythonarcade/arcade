import random
import math
import arcade

SCALE = 0.0015

class PlayerSprite(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.last_change_x = self.center_x
        self.facing = "right"

    def update(self):
        self.center_x += self.change_x

        if self.change_x < 0:
            if abs(self.last_change_x - self.center_x) > 0.016:
                self.cur_texture_index += 1
                if self.cur_texture_index > 30:
                    self.cur_texture_index = 20
                self.set_texture(self.cur_texture_index)
                self.last_change_x = self.center_x

        if self.change_x > 0:
            if abs(self.last_change_x - self.center_x) > 0.016:
                self.cur_texture_index += 1
                if self.cur_texture_index > 15:
                    self.cur_texture_index = 4
                self.set_texture(self.cur_texture_index)
                self.last_change_x = self.center_x

    def left(self):
        self.change_x = -0.003


    def face_left(self):
        if self.facing != "left":
            self.set_texture(20)
            self.facing = "left"

    def face_right(self):
        if self.facing != "right":
            self.set_texture(4)
            self.facing = "right"

    def right(self):
        self.change_x = 0.003

    def stop_left(self):
        if self.change_x < 0:
            self.change_x = 0

    def stop_right(self):
        if self.change_x > 0:
            self.change_x = 0


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

        image_location_list = [
            [365, 98, 69, 71],
            [0, 196, 66, 92],
            [438, 0, 69, 92],
            [438, 93, 67, 94],
            [67, 196, 66, 92],
            [0, 0, 72, 97],
            [73, 0, 72, 97],
            [146, 0, 72, 97],
            [0, 98, 72, 97],
            [73, 98, 72, 97],
            [146, 98, 72, 97],
            [219, 0, 72, 97],
            [292, 0, 72, 97],
            [219, 98, 72, 97],
            [365, 0, 72, 97],
            [292, 98, 72, 97]]

        texture_info_list = arcade.load_textures("images/p1_spritesheet.png", image_location_list)

        self.player_sprite = PlayerSprite()
        for texture_info in texture_info_list:
            texture, width, height = texture_info
            self.player_sprite.append_texture(texture, width, height)

        texture_info_list = arcade.load_textures("images/p1_spritesheet.png", image_location_list, True)

        for texture_info in texture_info_list:
            texture, width, height = texture_info
            self.player_sprite.append_texture(texture, width, height)

        self.player_sprite.scale = 0.003
        self.player_sprite.center_x = x_pos
        self.player_sprite.set_texture(4)
        x_pos += 0.15
        self.all_sprites_list.append(self.player_sprite)

    def render(self):
        arcade.start_render()

        self.all_sprites_list.draw()
        arcade.draw_text("Texture: {}".format(self.player_sprite.cur_texture_index), 0, -0.3, arcade.color.WHITE)

        arcade.swap_buffers()

    def key_pressed(self, key, x, y):
        if not self.player_sprite.respawning and key == b' ':
            pass

    def special_pressed(self, key, x, y):
        if key == arcade.key.LEFT:
            self.player_sprite.left()
            self.player_sprite.face_left()
        elif key == arcade.key.RIGHT:
            self.player_sprite.right()
            self.player_sprite.face_right()
        elif key == arcade.key.UP:
            self.player_sprite.thrust = .0005
        elif key == arcade.key.DOWN:
            self.player_sprite.thrust = -.0002

    def special_released(self, key, x, y):
        if key == arcade.key.LEFT:
            self.player_sprite.stop_left()
        elif key == arcade.key.RIGHT:
            self.player_sprite.stop_right()
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
