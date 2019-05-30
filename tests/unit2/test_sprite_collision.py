import arcade

def test_sprites_at_point():

    coin_list = arcade.SpriteList()
    sprite = arcade.Sprite("../../arcade/examples/images/coin_01.png")
    sprite.position = (130, 130)
    sprite.set_position(130, 130)
    sprite.angle = 90
    coin_list.append(sprite)

    sprite_list = arcade.get_sprites_at_point((0, 0), coin_list)
    assert len(sprite_list) == 0

    sprite_list = arcade.get_sprites_at_point((140, 130), coin_list)
    assert len(sprite_list) == 1
