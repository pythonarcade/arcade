import os
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LINE_HEIGHT = 20
CHARACTER_SCALING = 0.5

class MyTestWindow(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.frame_count = 0
        arcade.set_background_color(arcade.color.AMAZON)

        self.character_list = arcade.SpriteList()


        self.player = arcade.AnimatedWalkingSprite()

        character_scale = 1
        self.player.stand_right_textures = []
        self.player.stand_right_textures.append(arcade.load_texture("../../arcade/examples/images/character_sprites/character0.png",
                                                                    scale=character_scale))
        self.player.stand_left_textures = []
        self.player.stand_left_textures.append(arcade.load_texture("../../arcade/examples/images/character_sprites/character0.png",
                                                                   scale=character_scale, mirrored=True))

        self.player.walk_right_textures = []

        self.player.walk_right_textures.append(arcade.load_texture("../../arcade/examples/images/character_sprites/characterw0.png",
                                                                   scale=character_scale))
        self.player.walk_right_textures.append(arcade.load_texture("../../arcade/examples/images/character_sprites/characterw1.png",
                                                                   scale=character_scale))
        self.player.walk_right_textures.append(arcade.load_texture("../../arcade/examples/images/character_sprites/characterw2.png",
                                                                   scale=character_scale))
        self.player.walk_right_textures.append(arcade.load_texture("../../arcade/examples/images/character_sprites/characterw3.png",
                                                                   scale=character_scale))

        self.player.walk_left_textures = []

        self.player.walk_left_textures.append(arcade.load_texture("../../arcade/examples/images/character_sprites/characterw0.png",
                                                                  scale=character_scale, mirrored=True))
        self.player.walk_left_textures.append(arcade.load_texture("../../arcade/examples/images/character_sprites/characterw1.png",
                                                                  scale=character_scale, mirrored=True))
        self.player.walk_left_textures.append(arcade.load_texture("../../arcade/examples/images/character_sprites/characterw2.png",
                                                                  scale=character_scale, mirrored=True))
        self.player.walk_left_textures.append(arcade.load_texture("../../arcade/examples/images/character_sprites/characterw3.png",
                                                                  scale=character_scale, mirrored=True))

        self.player.texture_change_distance = 20

        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2
        self.player.scale = 0.8
        self.player.change_x = 2

        self.character_list.append(self.player)

        self.coin_list = arcade.SpriteList()
        sprite = arcade.Sprite("../../arcade/examples/images/coin_01.png", CHARACTER_SCALING)
        sprite.position = (130, 130)
        sprite.set_position(130, 130)
        sprite.angle = 90
        self.coin_list.append(sprite)

    def on_draw(self):
        arcade.start_render()
        self.coin_list.draw()
        self.character_list.draw()

    def update(self, delta_time):
        self.frame_count += 1
        if self.frame_count == 70:
            self.player.change_x *= -1
        self.coin_list.update()
        self.character_list.update()
        self.character_list.update_animation()


def test_sprite():
    window = MyTestWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Test Animation")
    window.test(150)
    window.close()
