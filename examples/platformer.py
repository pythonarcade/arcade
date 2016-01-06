import random
import math
import arcade

SCALE = 0.0011

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
            self.change_y -= 0.0015
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

    def set_left_walk_textures(self, texture_index_list):
        self.left_textures = texture_index_list

    def set_right_walk_textures(self, texture_index_list):
        self.right_textures = texture_index_list

    def set_left_jump_textures(self, texture_index_list):
        self.jump_left_textures = texture_index_list

    def set_right_jump_textures(self, texture_index_list):
        self.jump_right_textures = texture_index_list

    def set_left_stand_textures(self, texture_index_list):
        self.left_stand_textures = texture_index_list

    def set_right_stand_textures(self, texture_index_list):
        self.right_stand_textures = texture_index_list

    def left(self):
        self.change_x = -0.003

    def stop_left(self):
        if self.change_x < 0:
            self.change_x = 0
            self.set_texture(self.left_stand_textures[0])

    def right(self):
        self.change_x = 0.003

    def stop_right(self):
        if self.change_x > 0:
            self.change_x = 0
            self.set_texture(self.right_stand_textures[0])

    def face_left(self):
        if self.facing != "left":
            self.set_texture(self.left_textures[0])
            self.facing = "left"

    def face_right(self):
        if self.facing != "right":
            self.set_texture(self.right_textures[0])
            self.facing = "right"

    def jump(self):
        self.change_y = 0.03
        if self.facing == "right":
            self.set_texture(self.jump_right_textures[0])
        if self.facing == "left":
            self.set_texture(self.jump_left_textures[0])

class PlayerSprite(PlatformerCharacterSprite):
    def __init__(self):
        super().__init__()

        self.texture_change_distance = 0.016


        image_location_list = [
                            [520, 516, 128, 256],
                            [520, 258, 128, 256],
                            [520, 0, 128, 256],
                            [390, 1548, 128, 256],
                            [390, 1290, 128, 256],
                            [390, 516, 128, 256],
                            [390, 258, 128, 256]]

        texture_info_list = arcade.load_textures("images/spritesheet_complete.png", image_location_list)

        for texture_info in texture_info_list:
            texture, width, height = texture_info
            self.append_texture(texture, width, height)

        texture_info_list = arcade.load_textures("images/spritesheet_complete.png", image_location_list, True)

        for texture_info in texture_info_list:
            texture, width, height = texture_info
            self.append_texture(texture, width, height)

        self.set_left_walk_textures([12, 13])
        self.set_right_walk_textures([5, 6])

        self.set_left_jump_textures([10])
        self.set_right_jump_textures([3])

        self.set_left_stand_textures([11])
        self.set_right_stand_textures([4])

        self.scale = SCALE
        self.set_texture(4)
        self.facing = "right"

class Platform(arcade.Sprite):
    """ Platform class. """
    pass

class MyApplication(arcade.ArcadeApplication):
    """ Main application class. """

    def __init__(self):
        pass

    def setup_game(self):
        self.all_sprites_list = arcade.SpriteList()

        self.player_sprite = PlayerSprite()
        self.all_sprites_list.append(self.player_sprite)

        self.platform = Platform("images/spritesheet_complete.png", SCALE, 130, 1806, 128, 128)

        self.platform.center_y = -1 + (self.platform.height / 2)

        self.all_sprites_list.append(self.platform)

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
