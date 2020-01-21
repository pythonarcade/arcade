import os
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LINE_HEIGHT = 20
CHARACTER_SCALING = 0.5
COIN_SCALE = 0.5


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
        self.player.stand_right_textures.append(
            arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_idle.png",
                                scale=character_scale))
        self.player.stand_left_textures = []
        self.player.stand_left_textures.append(
            arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_idle.png",
                                scale=character_scale, mirrored=True))

        self.player.walk_right_textures = []

        self.player.walk_right_textures.append(
            arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_walk0.png",
                                scale=character_scale))
        self.player.walk_right_textures.append(
            arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_walk1.png",
                                scale=character_scale))
        self.player.walk_right_textures.append(
            arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_walk2.png",
                                scale=character_scale))
        self.player.walk_right_textures.append(
            arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_walk3.png",
                                scale=character_scale))

        self.player.walk_left_textures = []

        self.player.walk_left_textures.append(
            arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_walk0.png",
                                scale=character_scale, mirrored=True))
        self.player.walk_left_textures.append(
            arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_walk1.png",
                                scale=character_scale, mirrored=True))
        self.player.walk_left_textures.append(
            arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_walk2.png",
                                scale=character_scale, mirrored=True))
        self.player.walk_left_textures.append(
            arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_walk3.png",
                                scale=character_scale, mirrored=True))

        self.player.texture_change_distance = 20

        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2
        self.player.scale = 0.8
        self.player.change_x = 2
        self.player.texture = self.player.stand_left_textures[0]

        self.character_list.append(self.player)

        self.coin_list = arcade.SpriteList()

        coin = arcade.AnimatedTimeSprite(scale=0.5)
        coin.center_x = 500
        coin.center_y = 500

        coin.textures = []
        coin.textures.append(arcade.load_texture(":resources:images/items/gold_1.png", scale=COIN_SCALE))
        coin.textures.append(arcade.load_texture(":resources:images/items/gold_2.png", scale=COIN_SCALE))
        coin.textures.append(arcade.load_texture(":resources:images/items/gold_3.png", scale=COIN_SCALE))
        coin.textures.append(arcade.load_texture(":resources:images/items/gold_4.png", scale=COIN_SCALE))
        coin.textures.append(arcade.load_texture(":resources:images/items/gold_3.png", scale=COIN_SCALE))
        coin.textures.append(arcade.load_texture(":resources:images/items/gold_2.png", scale=COIN_SCALE))
        coin.set_texture(0)
        self.coin_list.append(coin)

    def on_draw(self):
        arcade.start_render()
        self.coin_list.draw()
        self.character_list.draw()

    def update(self, delta_time):
        self.frame_count += 1
        if self.frame_count == 70:
            self.player.change_x *= -1

        self.coin_list.update()
        self.coin_list.update_animation(delta_time)

        self.character_list.update()
        self.character_list.update_animation(delta_time)


def test_sprite():
    window = MyTestWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Test Animation")
    window.test(150)
    window.close()
