import arcade

CHARACTER_SCALING = 0.5
frame_counter = 0


def test_sprite(window: arcade.Window):
    arcade.set_background_color(arcade.color.AMAZON)
    window.clear()
    global frame_counter
    frame_counter = 0

    character_list = arcade.SpriteList()
    character_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
    character_sprite.center_x = 50
    character_sprite.center_y = 50
    character_sprite.change_x = 2
    character_sprite.change_y = 2
    character_list.append(character_sprite)

    character_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
    character_sprite.center_x = 150
    character_sprite.center_y = 50
    character_list.append(character_sprite)

    character_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
    character_sprite.center_x = 200
    character_sprite.center_y = 50
    character_sprite.angle = 45
    character_list.append(character_sprite)

    character_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
    character_sprite.center_x = 250
    character_sprite.center_y = 50
    character_sprite.angle = 90
    character_list.append(character_sprite)

    character_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
    character_sprite.center_x = 300
    character_sprite.center_y = 50
    character_sprite.angle = 180
    character_list.append(character_sprite)

    character_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
    character_sprite.center_x = 300
    character_sprite.center_y = 50
    character_sprite.angle = 90
    assert character_sprite.center_x == 300
    assert character_sprite.center_y == 50

    character_sprite.angle = 0
    assert character_sprite.center_x == 300
    assert character_sprite.center_y == 50

    character_list.append(character_sprite)

    coin_list = arcade.SpriteList()
    sprite = arcade.Sprite(":resources:images/items/coinGold.png", CHARACTER_SCALING)
    sprite.position = (130, 130)
    sprite.set_position(130, 130)
    sprite.angle = 90
    coin_list.append(sprite)

    individual_coin = arcade.Sprite(":resources:images/items/coinGold.png", CHARACTER_SCALING)
    individual_coin.position = (230, 230)

    def on_draw():
        arcade.start_render()
        coin_list.draw()
        character_list.draw()
        assert arcade.get_pixel(150, 50) == (191, 121, 88)

        assert arcade.get_pixel(230, 230) == (59, 122, 87)
        individual_coin.draw()
        assert arcade.get_pixel(230, 230) == (255, 204, 0)

        # Test for coin scaling
        if frame_counter < 5:
            assert arcade.get_pixel(130, 150) == (59, 122, 87)
        else:
            assert arcade.get_pixel(130, 150) == (227, 182, 2)

    def update(delta_time):
        global frame_counter
        coin_list.update()
        character_list.update()

        frame_counter += 1
        if frame_counter == 5:
            character_list.pop()
            coin_list[0].scale = 2.0

        coin_hit_list = arcade.check_for_collision_with_list(character_sprite, coin_list)
        for coin in coin_hit_list:
            coin.kill()

    window.on_draw = on_draw
    window.update = update
    window.test(10)
