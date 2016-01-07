import random
import math
import arcade

SCALE = 1/127
BLOCK_WIDTH = 10
BLOCK_HEIGHT = 10

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
        self.speed = 0.003
        self.gravity = 0.0015
        self.floor = 1.5

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        if self.center_y > self.floor:
            self.change_y -= self.gravity
        elif self.change_y != 0:
            self.change_y = 0
            self.center_y = self.floor
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
        self.change_x = -self.speed

    def stop_left(self):
        if self.change_x < 0:
            self.change_x = 0
            self.set_texture(self.left_stand_textures[0])

    def right(self):
        self.change_x = self.speed

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
        self.change_y = self.jump_speed
        if self.facing == "right":
            self.set_texture(self.jump_right_textures[0])
        if self.facing == "left":
            self.set_texture(self.jump_left_textures[0])

class PlayerSprite(PlatformerCharacterSprite):
    def __init__(self):
        super().__init__()

        self.texture_change_distance = 0.1
        self.speed = 0.05
        self.jump_speed = 0.11
        self.gravity = 0.005

        top_trim = 100

        image_location_list = [
                            [520, 516 + top_trim, 128, 256 - top_trim],
                            [520, 258 + top_trim, 128, 256 - top_trim],
                            [520, 0 + top_trim, 128, 256 - top_trim],
                            [390, 1548 + top_trim, 128, 256 - top_trim],
                            [390, 1290 + top_trim, 128, 256 - top_trim],
                            [390, 516 + top_trim, 128, 256 - top_trim],
                            [390, 258 + top_trim, 128, 256 - top_trim]]

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
        self.player_sprite.transparent = False
        self.all_sprites_list.append(self.player_sprite)
        self.player_sprite.bottom = 3
        print(self.player_sprite.center_y)
        self.player_sprite.center_y = 1.62
        self.player_sprite.floor = 1.62
        self.player_sprite.center_x = BLOCK_WIDTH / 2

        for x in range(BLOCK_WIDTH):
            platform = Platform("images/spritesheet_complete.png", SCALE, 130, 1806, 128, 128)
            platform.center_x = 0.5 + x
            platform.center_y = 0.5
            self.all_sprites_list.append(platform)

    def render(self):
        arcade.start_render()

        self.all_sprites_list.draw()
        arcade.draw_text("Texture: {}".format(self.player_sprite.cur_texture_index), 0, -0.3, arcade.color.WHITE)
        grid_color = (0, 0, 255, 127)

        for y in range(0, BLOCK_HEIGHT):
            arcade.draw_line(0, y, BLOCK_WIDTH, y, grid_color)
        for x in range(0, BLOCK_WIDTH):
            arcade.draw_line(x, 0, x, BLOCK_HEIGHT, grid_color)


        arcade.swap_buffers()

    def key_pressed(self, key, x, y):
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

    def animate(self):

        self.all_sprites_list.update()
        arcade.redisplay()

    def run(self):

        self.open_window(800, 800)
        arcade.set_background_color((127, 127, 255))
        arcade.set_ortho(0, BLOCK_WIDTH, 0, BLOCK_HEIGHT)
        self.setup_game()

        arcade.run()

app = MyApplication()
app.run()
