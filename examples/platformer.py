import random
import math
import arcade

SCALE = 0.0015

class PlayerSprite(arcade.Sprite):
	pass

class MyApplication(arcade.ArcadeApplication):
    """ Main application class. """

    def __init__(self):
        pass

    def setup_game(self):
        self.all_sprites_list = arcade.SpriteList()

        player = PlayerSprite()
        texture, width, height = arcade.load_texture("images/p1_spritesheet.png", 0, 0, 100, 100)
        player.append_texture(texture)
        player.set_texture(0)
        player.width = 0.3
        player.height = 0.3
        self.all_sprites_list.append(player)

    def render(self):
        arcade.start_render()

        self.all_sprites_list.draw()

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
