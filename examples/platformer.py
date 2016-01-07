import random
import math
import arcade

SCALE = 1/127
BLOCK_WIDTH = 10
BLOCK_HEIGHT = 10

class PlayerSprite(arcade.PlatformerSpriteSheetSprite):
    def __init__(self):
        super().__init__()

        self.texture_change_distance = 0.1
        self.speed = 0.05
        self.jump_speed = 0.15

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
        self.apply_gravity = True

class Platform(arcade.Sprite):
    """ Platform class. """
    pass


class MyApplication(arcade.ArcadeApplication):
    """ Main application class. """

    def __init__(self):
        self.ortho_left = 0

    def setup_game(self):
        # Create sprite lists
        self.all_sprites_list = arcade.SpriteList()
        self.physics_engine = arcade.PlatformerPhysicsEngine()
        # Create player sprite
        self.player_sprite = PlayerSprite()
        # self.player_sprite.transparent = False
        self.player_sprite.bottom = 3
        self.player_sprite.center_y = 1.62
        self.player_sprite.floor = 1.62
        self.player_sprite.center_x = BLOCK_WIDTH / 2

        self.all_sprites_list.append(self.player_sprite)
        self.physics_engine.append(self.player_sprite)


        # Create platforms for floor
        for x in range(BLOCK_WIDTH * 2):
            platform = Platform("images/spritesheet_complete.png", SCALE, 130, 1806, 128, 128)
            platform.center_x = 0.5 + x
            platform.center_y = 0.5
            self.all_sprites_list.append(platform)
            self.physics_engine.append(platform)

        # Make a box
        platform = Platform("images/spritesheet_complete.png", SCALE, 2340, 1690, 128, 128)
        platform.center_x = 8.5
        platform.center_y = 1.5
        self.all_sprites_list.append(platform)
        self.physics_engine.append(platform)

        # Create a platform to jump onto
        platform = Platform("images/spritesheet_complete.png", SCALE, 1430, 780, 128, 70)
        platform.center_x = 3.5
        platform.center_y = 3.5
        self.all_sprites_list.append(platform)
        self.physics_engine.append(platform)

        platform = Platform("images/spritesheet_complete.png", SCALE, 1430, 650, 128, 70)
        platform.center_x = 4.5
        platform.center_y = 3.5
        self.all_sprites_list.append(platform)
        self.physics_engine.append(platform)

        platform = Platform("images/spritesheet_complete.png", SCALE, 1430, 520, 128, 70)
        platform.center_x = 5.5
        platform.center_y = 3.5
        self.all_sprites_list.append(platform)
        self.physics_engine.append(platform)

        # Create another platform to jump onto
        platform = Platform("images/spritesheet_complete.png", SCALE, 1430, 130, 128, 128)
        platform.center_x = 5.5
        platform.center_y = 6
        self.all_sprites_list.append(platform)
        self.physics_engine.append(platform)

        platform = Platform("images/spritesheet_complete.png", SCALE, 1430, 0, 128, 128)
        platform.center_x = 6.5
        platform.center_y = 6
        self.all_sprites_list.append(platform)
        self.physics_engine.append(platform)

        platform = Platform("images/spritesheet_complete.png", SCALE, 1300, 1820, 128, 128)
        platform.center_x = 7.5
        platform.center_y = 6
        self.all_sprites_list.append(platform)
        self.physics_engine.append(platform)

    def render(self):
        arcade.start_render()

        self.all_sprites_list.draw()

        # grid_color = (0, 0, 255, 127)

        # for y in range(0, BLOCK_HEIGHT):
        #     arcade.draw_line(0, y, BLOCK_WIDTH, y, grid_color)
        # for x in range(0, BLOCK_WIDTH):
        #     arcade.draw_line(x, 0, x, BLOCK_HEIGHT, grid_color)

        arcade.swap_buffers()

    def key_pressed(self, key, x, y):
        pass

    def special_pressed(self, key, x, y):
        if key == arcade.key.LEFT:
            self.player_sprite.go_left()
            self.player_sprite.face_left()
        elif key == arcade.key.RIGHT:
            self.player_sprite.go_right()
            self.player_sprite.face_right()
        elif key == arcade.key.UP:
            self.player_sprite.jump()

    def special_released(self, key, x, y):
        if key == arcade.key.LEFT:
            self.player_sprite.stop_left()
        elif key == arcade.key.RIGHT:
            self.player_sprite.stop_right()

    def animate(self):

        self.physics_engine.update()

        if self.player_sprite.center_x - self.ortho_left > 7:
            self.ortho_left = self.player_sprite.center_x - 7
            arcade.set_ortho(self.ortho_left, BLOCK_WIDTH + self.ortho_left, 0, BLOCK_HEIGHT)

        if self.player_sprite.center_x - self.ortho_left < 3:
            self.ortho_left = self.player_sprite.center_x - 3
            arcade.set_ortho(self.ortho_left, BLOCK_WIDTH + self.ortho_left, 0, BLOCK_HEIGHT)

        arcade.redisplay()

    def run(self):

        self.open_window(800, 800)
        arcade.set_background_color((127, 127, 255))
        arcade.set_ortho(self.ortho_left, BLOCK_WIDTH + self.ortho_left, 0, BLOCK_HEIGHT)
        self.setup_game()

        arcade.run()

app = MyApplication()
app.run()
