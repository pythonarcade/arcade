import pytest
import arcade

COIN_SCALE = 0.5
frame_count = 0


def test_sprite_animated_old(window: arcade.Window):
    global frame_count
    frame_count = 0
    SCREEN_WIDTH = window.width
    SCREEN_HEIGHT = window.height
    arcade.set_background_color(arcade.color.AMAZON)

    character_list = arcade.SpriteList()

    player = arcade.AnimatedWalkingSprite()

    player.scale = 1
    player.stand_right_textures = []
    player.stand_right_textures.append(
        arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_idle.png"))
    player.stand_left_textures = []
    player.stand_left_textures.append(
        arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_idle.png", flipped_horizontally=True))

    player.walk_right_textures = []

    player.walk_right_textures.append(
        arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_walk0.png"))
    player.walk_right_textures.append(
        arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_walk1.png"))
    player.walk_right_textures.append(
        arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_walk2.png"))
    player.walk_right_textures.append(
        arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_walk3.png"))

    player.walk_left_textures = []

    player.walk_left_textures.append(
        arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_walk0.png",
                            flipped_horizontally=True))
    player.walk_left_textures.append(
        arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_walk1.png",
                            flipped_horizontally=True))
    player.walk_left_textures.append(
        arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_walk2.png",
                            flipped_horizontally=True))
    player.walk_left_textures.append(
        arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_walk3.png",
                            flipped_horizontally=True))

    player.texture_change_distance = 20

    player.center_x = SCREEN_WIDTH // 2
    player.center_y = SCREEN_HEIGHT // 2
    player.scale = 0.8
    player.change_x = 2
    player.texture = player.stand_left_textures[0]

    character_list.append(player)

    coin_list = arcade.SpriteList()

    with pytest.deprecated_call():
        coin = arcade.AnimatedTimeSprite(scale=0.5)

    coin.center_x = 500
    coin.center_y = 500

    coin.textures = []
    coin.textures.append(arcade.load_texture(":resources:images/items/gold_1.png"))
    coin.textures.append(arcade.load_texture(":resources:images/items/gold_2.png"))
    coin.textures.append(arcade.load_texture(":resources:images/items/gold_3.png"))
    coin.textures.append(arcade.load_texture(":resources:images/items/gold_4.png"))
    coin.textures.append(arcade.load_texture(":resources:images/items/gold_3.png"))
    coin.textures.append(arcade.load_texture(":resources:images/items/gold_2.png"))
    coin.scale = COIN_SCALE

    coin.set_texture(0)
    coin_list.append(coin)

    def on_draw():
        arcade.start_render()
        coin_list.draw()
        character_list.draw()

    def update(delta_time):
        global frame_count
        frame_count += 1
        if frame_count == 70:
            player.change_x *= -1

        coin_list.update()
        coin_list.update_animation(delta_time)

        character_list.update()
        character_list.update_animation(delta_time)

    window.on_draw = on_draw
    window.update = update
    window.test(150)
