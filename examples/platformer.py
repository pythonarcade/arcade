import random
import math
import arcade

SCALE = 0.0015

class PlatformerCharacterSprite(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.last_change_x = self.center_x
        self.facing = "right"
        self.left_textures = []
        self.right_textures = []
        self.up_textures = []
        self.down_textures = []
        self.jump_textures = []
        self.cur_texture_index = 0
        self.texture_change_distance = 0

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        if self.center_y > 0:
            self.change_y -= 0.003
        elif self.change_y != 0:
            self.change_y = 0
            self.center_y = 0
            if self.facing == "right":
                self.set_texture(self.right_textures[0])
            if self.facing == "left":
                self.set_texture(self.left_textures[0])            

        if self.change_y == 0.0:
            if self.change_x < 0:
                if abs(self.last_change_x - self.center_x) > self.texture_change_distance:
                    if self.cur_texture_index in self.left_textures:
                        pos = self.left_textures.index(self.cur_texture_index) + 1
                    else:
                        pos = 0
                    if pos >= len(self.left_textures):
                        pos = 0
                    self.set_texture(self.left_textures[pos])
                    self.last_change_x = self.center_x

            if self.change_x > 0:
                if abs(self.last_change_x - self.center_x) > self.texture_change_distance:
                    if self.cur_texture_index in self.right_textures:
                        pos = self.right_textures.index(self.cur_texture_index) + 1
                    else:
                        pos = 0
                    if pos >= len(self.right_textures):
                        pos = 0
                    self.set_texture(self.right_textures[pos])
                    self.last_change_x = self.center_x

    def set_left_textures(self, texture_index_list):
        self.left_textures = texture_index_list

    def set_right_textures(self, texture_index_list):
        self.right_textures = texture_index_list

    def left(self):
        self.change_x = -0.003

    def stop_left(self):
        if self.change_x < 0:
            self.change_x = 0

    def right(self):
        self.change_x = 0.003

    def stop_right(self):
        if self.change_x > 0:
            self.change_x = 0

    def face_left(self):
        if self.facing != "left":
            self.set_texture(20)
            self.facing = "left"

    def face_right(self):
        if self.facing != "right":
            self.set_texture(4)
            self.facing = "right"

    def jump(self):
        self.change_y = 0.05
        if self.facing == "right":
            self.set_texture(3)
        if self.facing == "left":
            self.set_texture(19)

class PlayerSprite(PlatformerCharacterSprite):
    def __init__(self):
        super().__init__()

        self.texture_change_distance = 0.016

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

        for texture_info in texture_info_list:
            texture, width, height = texture_info
            self.append_texture(texture, width, height)

        texture_info_list = arcade.load_textures("images/p1_spritesheet.png", image_location_list, True)

        for texture_info in texture_info_list:
            texture, width, height = texture_info
            self.append_texture(texture, width, height)

        self.set_left_textures([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30])
        self.set_right_textures([4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        self.scale = 0.003
        self.set_texture(4)        

class MyApplication(arcade.ArcadeApplication):
    """ Main application class. """

    def __init__(self):
        pass

    def setup_game(self):
        self.all_sprites_list = arcade.SpriteList()

        self.player_sprite = PlayerSprite()

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
            self.player_sprite.jump()
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
