import random
import math
import arcade
import copy

SCALE = 1/127
BLOCK_WIDTH = 10
BLOCK_HEIGHT = 10

class PlayerSprite(arcade.PlatformerSpriteSheetSprite):
    def __init__(self):
        super().__init__()

        self.texture_change_distance = 0.2
        self.speed = 0.05
        self.jump_speed = 0.15

        top_trim = 100
        left_trim = 2
        right_trim = 2
        image_location_list = [
                            [520 + left_trim, 516 + top_trim, 128 - left_trim - right_trim, 256 - top_trim],
                            [520 + left_trim, 258 + top_trim, 128 - left_trim - right_trim, 256 - top_trim],
                            [520 + left_trim, 0 + top_trim, 128 - left_trim - right_trim, 256 - top_trim],
                            [390 + left_trim, 1548 + top_trim, 128 - left_trim - right_trim, 256 - top_trim],
                            [390 + left_trim, 1290 + top_trim, 128 - left_trim - right_trim, 256 - top_trim],
                            [390 + left_trim, 516 + top_trim, 128 - left_trim - right_trim, 256 - top_trim],
                            [390 + left_trim, 258 + top_trim, 128 - left_trim - right_trim, 256 - top_trim]]

        texture_info_list = arcade.load_textures("images/spritesheet_complete.png", image_location_list)

        for texture_info in texture_info_list:
            texture = texture_info
            self.append_texture(texture)

        texture_info_list = arcade.load_textures("images/spritesheet_complete.png", image_location_list, True)

        for texture_info in texture_info_list:
            texture = texture_info
            self.append_texture(texture)

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

class MovingPlatform(Platform):
    def __init__(self, filename=None, scale=0, x=0, y=0, width=0, height=0):
        super().__init__(filename, scale, x, y, width, height)
        self.left_boundary = 0
        self.right_boundary = 0

    def update(self):
        super().update()
        if self.center_x < self.left_boundary and self.change_x < 0:
            self.change_x *= -1
        if self.center_x > self.right_boundary and self.change_x > 0:
            self.change_x *= -1

class MyApplication(arcade.ArcadeApplication):
    """ Main application class. """

    def __init__(self):
        self.ortho_left = 0

    def create_platform(self, template, x, y):
        platform = copy.copy(template)
        platform.set_position(x, y)
        self.all_sprites_list.append(platform)
        self.physics_engine.append(platform)
        return platform

    def create_coin(self, template, x, y):
        platform = copy.copy(template)
        platform.set_position(x, y)
        self.all_sprites_list.append(platform)
        self.coin_list.append(platform)
        return platform

    def setup_game(self):
        # Create sprite lists
        self.all_sprites_list = arcade.SpriteList()
        self.physics_engine = arcade.PlatformerPhysicsEngine()
        self.coin_list = arcade.SpriteList()

        # Create player sprite
        self.player_sprite = PlayerSprite()
        # self.player_sprite.transparent = False
        self.player_sprite.bottom = 3
        self.player_sprite.center_y = 1.62
        self.player_sprite.floor = 1.62
        self.player_sprite.center_x = BLOCK_WIDTH / 2

        self.score = 0

        self.all_sprites_list.append(self.player_sprite)
        self.physics_engine.append(self.player_sprite)

        # Create sprite templates
        stone_floor_template = Platform("images/spritesheet_complete.png", SCALE, 130, 1806, 128, 128)
        box_template = Platform("images/spritesheet_complete.png", SCALE, 2340, 1690, 128, 128)
        platform_left = Platform("images/spritesheet_complete.png", SCALE, 1430, 780, 128, 70)
        platform_mid = Platform("images/spritesheet_complete.png", SCALE, 1430, 650, 128, 70)
        platform_right = Platform("images/spritesheet_complete.png", SCALE, 1430, 520, 128, 70)
        coin = arcade.Sprite("images/spritesheet_complete.png", SCALE, 2762, 162, 65, 65)

        # Create platforms for floor
        for x in range(BLOCK_WIDTH * 2):
            self.create_platform(stone_floor_template, .5 + x, 0.5)

        # Make a box wall
        for y in range(5):
            self.create_platform(box_template, 0.5, y + 1.5)

        # Make a box wall
        for y in range(3):
            self.create_platform(box_template, 8.5, y + 1.5)

        # Coins right before the wall
        self.create_coin(coin, 7.5, 1.5)

        # Create a platform to jump onto
        self.create_platform(platform_left, 4.5, 3.0)
        self.create_platform(platform_mid, 5.5, 3.0)
        self.create_platform(platform_right, 6.5, 3.0)

        # Create another platform to jump onto
        self.create_platform(platform_left, 5.5, 5.5)
        self.create_platform(platform_mid, 6.5, 5.5)
        self.create_platform(platform_right, 7.5, 5.5)

        # Coins on the platform
        self.create_coin(coin, 5.5, 6.5)
        self.create_coin(coin, 6.5, 6.5)
        self.create_coin(coin, 7.5, 6.5)

        # Coins in an arc after the platform
        # and over the box wall
        self.create_coin(coin, 8.5, 7)
        self.create_coin(coin, 9.5, 8)
        self.create_coin(coin, 10.5, 8)
        self.create_coin(coin, 11.5, 7)

        # Create another platform to jump onto
        self.create_platform(platform_left, 13, 3.5)
        self.create_platform(platform_mid, 14, 3.5)
        self.create_platform(platform_right, 15, 3.5)

        self.create_coin(coin, 13, 4.5)
        self.create_coin(coin, 14, 4.5)
        self.create_coin(coin, 15, 4.5)

        # Create another platform to jump onto
        self.create_platform(platform_left, 18, 3)
        self.create_platform(platform_mid, 19, 3)
        self.create_platform(platform_right, 20, 3)

        self.create_coin(coin, 18, 4)
        self.create_coin(coin, 19, 4)
        self.create_coin(coin, 20, 4)

        moving_platform = MovingPlatform("images/spritesheet_complete.png", SCALE, 1430, 650, 128, 70)
        moving_platform.set_position(2, 7)
        moving_platform.left_boundary = 3
        moving_platform.right_boundary = 8
        moving_platform.change_x = .01
        self.all_sprites_list.append(moving_platform)
        self.physics_engine.append(moving_platform)



    def render(self):
        arcade.start_render()

        self.all_sprites_list.draw()

        arcade.draw_text("Score: {}".format(self.score), self.ortho_left + 0.01, 9.75, arcade.color.BLACK)

        # grid_color = (0, 0, 255, 127)

        # for y in range(0, BLOCK_HEIGHT):
        #     arcade.draw_line(0, y, BLOCK_WIDTH, y, grid_color)
        # for x in range(0, BLOCK_WIDTH):
        #     arcade.draw_line(x, 0, x, BLOCK_HEIGHT, grid_color)

        arcade.finish_render()

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
            if self.player_sprite.change_y == 0:
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
            arcade.set_viewport(self.ortho_left, BLOCK_WIDTH + self.ortho_left, 0, BLOCK_HEIGHT)

        if self.player_sprite.center_x - self.ortho_left < 3:
            self.ortho_left = self.player_sprite.center_x - 3
            arcade.set_viewport(self.ortho_left, BLOCK_WIDTH + self.ortho_left, 0, BLOCK_HEIGHT)

        coins_hit = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)
        for coin in coins_hit:
            coin.kill()
            self.score += 1

        #arcade.draw_text("Score: {}".format(self.score), 5, 5, arcade.color.BLACK)
        arcade.redisplay()

    def run(self):

        self.open_window(800, 800)
        arcade.set_background_color((127, 127, 255))
        arcade.set_viewport(self.ortho_left, BLOCK_WIDTH + self.ortho_left, 0, BLOCK_HEIGHT)
        self.setup_game()

        arcade.run()

app = MyApplication()
app.run()
