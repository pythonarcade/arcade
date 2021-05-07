import os
import pytest
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LINE_HEIGHT = 20
CHARACTER_SCALING = 0.5
COIN_SCALE = 0.25


def test_load_textures(window):
    arcade.set_background_color(arcade.color.AMAZON)
    frame_count = 0

    character_list = arcade.SpriteList()
    player = arcade.AnimatedWalkingSprite()

    player.stand_right_textures = [arcade.load_texture(":resources:images/animated_characters/robot/robot_idle.png")]
    player.stand_left_textures = [arcade.load_texture(":resources:images/animated_characters/robot/robot_idle.png", flipped_horizontally=True)]

    player.walk_right_textures = [
        arcade.load_texture(":resources:images/animated_characters/robot/robot_walk0.png"),
        arcade.load_texture(":resources:images/animated_characters/robot/robot_walk1.png"),
        arcade.load_texture(":resources:images/animated_characters/robot/robot_walk2.png"),
        arcade.load_texture(":resources:images/animated_characters/robot/robot_walk3.png"),
        arcade.load_texture(":resources:images/animated_characters/robot/robot_walk4.png"),
        arcade.load_texture(":resources:images/animated_characters/robot/robot_walk5.png"),
        arcade.load_texture(":resources:images/animated_characters/robot/robot_walk6.png"),
        arcade.load_texture(":resources:images/animated_characters/robot/robot_walk7.png")
    ]

    player.walk_left_textures = [
        arcade.load_texture(":resources:images/animated_characters/robot/robot_walk0.png", flipped_horizontally=True),
        arcade.load_texture(":resources:images/animated_characters/robot/robot_walk1.png", flipped_horizontally=True),
        arcade.load_texture(":resources:images/animated_characters/robot/robot_walk2.png", flipped_horizontally=True),
        arcade.load_texture(":resources:images/animated_characters/robot/robot_walk3.png", flipped_horizontally=True),
        arcade.load_texture(":resources:images/animated_characters/robot/robot_walk4.png", flipped_horizontally=True),
        arcade.load_texture(":resources:images/animated_characters/robot/robot_walk5.png", flipped_horizontally=True),
        arcade.load_texture(":resources:images/animated_characters/robot/robot_walk6.png", flipped_horizontally=True),
        arcade.load_texture(":resources:images/animated_characters/robot/robot_walk7.png", flipped_horizontally=True)
    ]

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
        if frame_count == 70:
            player.change_x *= -1

        coin_list.update()
        coin_list.update_animation(delta_time)

        character_list.update()
        character_list.update_animation(delta_time)

    for i in range(90):
        update(1/60)
        on_draw()
        window.flip()
        frame_count += 1
