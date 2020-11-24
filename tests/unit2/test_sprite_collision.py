import os
import arcade


def test_sprites_at_point():

    coin_list = arcade.SpriteList()
    sprite = arcade.SpriteSolidColor(50, 50, arcade.csscolor.RED)
    coin_list.append(sprite)

    # print()
    # print(sprite.points)
    sprite_list = arcade.get_sprites_at_point((0, 0), coin_list)
    assert len(sprite_list) == 1

    sprite.position = (130, 130)
    # print()
    # print(sprite.points)

    sprite_list = arcade.get_sprites_at_point((0, 0), coin_list)
    assert len(sprite_list) == 0

    sprite_list = arcade.get_sprites_at_point((140, 130), coin_list)
    assert len(sprite_list) == 1

    sprite.angle = 90
    # print()
    # print(sprite.points)

    sprite_list = arcade.get_sprites_at_point((0, 0), coin_list)
    assert len(sprite_list) == 0

    sprite_list = arcade.get_sprites_at_point((140, 130), coin_list)
    assert len(sprite_list) == 1


def test_sprite_collides_with_point():
    sprite = arcade.Sprite(center_x=0, center_y=0)
    sprite.width = 2
    sprite.height = 2

    # Affirmative
    point = (0, 0)
    assert sprite.collides_with_point(point) is True
    point = (0, 0.9)
    assert sprite.collides_with_point(point) is True
    point = (0.9, 0)
    assert sprite.collides_with_point(point) is True
    point = (0.9, 0.9)
    assert sprite.collides_with_point(point) is True

    # Negative
    point = (0, 1)
    assert sprite.collides_with_point(point) is False
    point = (1, 0)
    assert sprite.collides_with_point(point) is False
    point = (1, 1)
    assert sprite.collides_with_point(point) is False
    point = (-1, -1)
    assert sprite.collides_with_point(point) is False
    point = (-1, 0)
    assert sprite.collides_with_point(point) is False
    point = (2, 2)
    assert sprite.collides_with_point(point) is False


def test_sprite_collides_with_sprite():
    sprite_one = arcade.Sprite(center_x=0, center_y=0)
    sprite_one.width = 10
    sprite_one.height = 10

    sprite_two = arcade.Sprite(center_x=0, center_y=0)
    sprite_two.width = 10
    sprite_two.height = 10

    sprite_three = arcade.Sprite(center_x=0, center_y=0)
    sprite_three.width = 1
    sprite_three.height = 1

    # Exact overlap
    assert sprite_one.collides_with_sprite(sprite_two) is True

    # Contains
    assert sprite_one.collides_with_sprite(sprite_three) is True

    # Complete overlap
    assert sprite_three.collides_with_sprite(sprite_one) is True

    # Far away
    sprite_two.center_x = 100
    assert sprite_one.collides_with_sprite(sprite_two) is False

    # border to the right
    sprite_two.center_x = 10
    assert sprite_one.collides_with_sprite(sprite_two) is False


    # Borders, opposite side
    sprite_two.center_x = -10
    assert sprite_one.collides_with_sprite(sprite_two) is False

    # Overlap
    sprite_two.center_x = -9
    assert sprite_one.collides_with_sprite(sprite_two) is True


def test_sprite_collides_with_list():
    coins = arcade.SpriteList()
    for x in range(0, 50, 10):
        coin = arcade.Sprite(center_x=x, center_y=0)
        coin.width = 10
        coin.height = 10
        coins.append(coin)

    player = arcade.Sprite(center_x=100, center_y=100)
    player.width = 10
    player.height = 10

    # collides with none
    result = player.collides_with_list(coins)
    assert len(result) == 0, "Should return empty list"

    # collides with one
    player.center_x = -5
    player.center_y = 0
    result = player.collides_with_list(coins)
    assert len(result) == 1, "Should collide with one"

    # collides with two
    player.center_x = 5
    result = player.collides_with_list(coins)
    assert len(result) == 2, "Should collide with two"
