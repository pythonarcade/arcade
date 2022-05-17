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

    def on_draw():
        arcade.start_render()
        character_list.draw()

    def update(delta_time):
        if frame_count == 70:
            player.change_x *= -1

        character_list.update()
        character_list.update_animation(delta_time)

    for i in range(90):
        update(1/60)
        on_draw()
        window.flip()
        frame_count += 1


def  test_load_spritesheet():
    textures = arcade.load_spritesheet(
        ":resources:images/spritesheets/codepage_437.png",
        sprite_width=9,
        sprite_height=16,
        columns=32,
        count=32*9,
        hit_box_algorithm=None,
    )
    assert len(textures) == 32 * 9
    assert textures[0].image.size  == (9, 16)

    # Check the byte data of some simple characters
    # First character is white with 0 alpha
    assert textures[0].image.tobytes() == b'\xff\xff\xff\x00' * 9 * 16
    # last tile is just 0 bytes (Not even a character)
    assert textures[-1].image.tobytes() == b'\x00\x00\x00\x00' * 9 * 16
    # Char 219 is completely white
    assert textures[219].image.tobytes() == b'\xff\xff\xff\xff' * 9 * 16
    # The dot letter has 140 black and 4 white pixels
    assert textures[46].image.tobytes().count(b'\xff\xff\xff\x00')  == 140
    assert textures[46].image.tobytes().count(b'\xff\xff\xff\xff')  == 4
