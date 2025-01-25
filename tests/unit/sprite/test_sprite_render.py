"""
Rendering tests for Sprite
"""

import arcade

SPRITE_TEXTURE_FEMALE_PERSON_IDLE = arcade.load_texture(
    ":resources:images/animated_characters/female_person/femalePerson_idle.png"
)
SPRITE_TEXTURE_GOLD_COIN = arcade.load_texture(":resources:images/items/coinGold.png")


def test_draw_lazy_spritelist(window: arcade.Window):
    """Test that a lazy sprite list is drawn correctly"""
    sprite = arcade.Sprite(SPRITE_TEXTURE_GOLD_COIN)
    sprite_list = arcade.SpriteList(lazy=True)
    sprite_list.append(sprite)
    # Should not crash
    sprite_list.draw()


def test_render_simple(window):
    """Simple sprite rendering test"""
    window.background_color = arcade.color.AMAZON
    sprite = arcade.Sprite(SPRITE_TEXTURE_GOLD_COIN)
    sprite.position = 50, 50

    sprite_list = arcade.SpriteList()
    sprite_list.append(sprite)

    def on_draw():
        window.clear()
        assert arcade.get_pixel(50, 50, components=4) == arcade.color.AMAZON
        sprite_list.draw()
        assert arcade.get_pixel(50, 50) == (255, 204, 0)

    window.draw = on_draw
    window.test(2)


def test_render_with_movement(window: arcade.Window):
    """Render dynamic sprites and verify"""
    CHARACTER_SCALING = 0.5
    window.background_color = arcade.color.AMAZON
    window.clear()
    global frame_counter
    frame_counter = 0

    character_list = arcade.SpriteList()
    character_sprite = arcade.Sprite(SPRITE_TEXTURE_FEMALE_PERSON_IDLE, scale=CHARACTER_SCALING)
    character_sprite.center_x = 50
    character_sprite.center_y = 50
    character_sprite.change_x = 2
    character_sprite.change_y = 2
    character_list.append(character_sprite)

    character_sprite = arcade.Sprite(SPRITE_TEXTURE_FEMALE_PERSON_IDLE, scale=CHARACTER_SCALING)
    character_sprite.center_x = 150
    character_sprite.center_y = 50
    character_list.append(character_sprite)

    character_sprite = arcade.Sprite(SPRITE_TEXTURE_FEMALE_PERSON_IDLE, scale=CHARACTER_SCALING)
    character_sprite.center_x = 200
    character_sprite.center_y = 50
    character_sprite.angle = 45
    character_list.append(character_sprite)

    character_sprite = arcade.Sprite(SPRITE_TEXTURE_FEMALE_PERSON_IDLE, scale=CHARACTER_SCALING)
    character_sprite.center_x = 250
    character_sprite.center_y = 50
    character_sprite.angle = 90
    character_list.append(character_sprite)

    character_sprite = arcade.Sprite(SPRITE_TEXTURE_FEMALE_PERSON_IDLE, scale=CHARACTER_SCALING)
    character_sprite.center_x = 300
    character_sprite.center_y = 50
    character_sprite.angle = 180
    character_list.append(character_sprite)

    character_sprite = arcade.Sprite(SPRITE_TEXTURE_FEMALE_PERSON_IDLE, scale=CHARACTER_SCALING)
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
    sprite = arcade.Sprite(SPRITE_TEXTURE_GOLD_COIN, scale=CHARACTER_SCALING)
    sprite.position = (130, 130)
    sprite.angle = 90
    coin_list.append(sprite)

    individual_coin = arcade.Sprite(SPRITE_TEXTURE_GOLD_COIN, scale=CHARACTER_SCALING)
    individual_coin.position = (230, 230)

    def on_draw():
        window.clear()
        coin_list.draw()
        character_list.draw()
        assert arcade.get_pixel(150, 50) == (191, 121, 88)

        assert arcade.get_pixel(230, 230) == (59, 122, 87)
        arcade.draw_sprite(individual_coin)
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
    window.on_update = update
    window.test(10)


def test_render_sprite_solid_pixels(window: arcade.Window):
    """Render solid color sprite and sample multiple pixels to verify color is correct"""
    SIZE = 50
    SPACING = SIZE * 2
    ROW_SPACING = 100
    window.background_color = arcade.color.BLACK

    character_list = arcade.SpriteList()

    for i in range(7):
        my_width = SIZE
        my_height = SIZE + i * 3
        my_color = (i * 40, 0, 255)
        center_x = SPACING + (i * SPACING)
        center_y = ROW_SPACING
        character_sprite = arcade.SpriteSolidColor(my_width, my_height, color=my_color)
        character_sprite.center_x = center_x
        character_sprite.center_y = center_y
        character_list.append(character_sprite)

    for i in range(7):
        my_width = SIZE + i * 3
        my_height = SIZE
        my_color = (0, i * 40, 255)
        center_x = SPACING + (i * SPACING)
        center_y = ROW_SPACING * 2
        character_sprite = arcade.SpriteSolidColor(my_width, my_height, color=my_color)
        character_sprite.center_x = center_x
        character_sprite.center_y = center_y
        character_list.append(character_sprite)

    def on_draw():
        window.clear()
        character_list.draw()

        for i in range(7):
            my_width = SIZE
            my_height = SIZE + i * 3
            my_color = (i * 40, 0, 255)
            center_x = SPACING + (i * SPACING)
            center_y = ROW_SPACING

            # Sample bottom
            pixel_color = arcade.get_pixel(center_x, center_y - (my_height // 2 - 4))
            assert pixel_color == my_color

            # Sample top
            pixel_color = arcade.get_pixel(center_x, center_y + (my_height // 2 - 4))
            assert pixel_color == my_color

            # Sample right
            pixel_color = arcade.get_pixel(center_x + (my_width // 2 - 4), center_y)
            assert pixel_color == my_color

        for i in range(7):
            my_width = SIZE + i * 3
            my_height = SIZE
            my_color = (0, i * 40, 255)
            center_x = SPACING + (i * SPACING)
            center_y = ROW_SPACING * 2

            # Sample bottom
            pixel_color = arcade.get_pixel(center_x, center_y - (my_height // 2 - 4))
            assert pixel_color == my_color

            # Sample top
            pixel_color = arcade.get_pixel(center_x, center_y + (my_height // 2 - 4))
            assert pixel_color == my_color

    window.on_draw = on_draw
    window.test()


def test_render_scaled(window):
    """Render scaled sprites and verify"""
    CHARACTER_SCALING = 0.5
    window.background_color = arcade.color.AMAZON

    # ensure normal scaling works correctly
    gold_1 = arcade.Sprite(":resources:/images/items/gold_1.png")
    assert gold_1.scale == (1.0, 1.0)
    assert gold_1.width, gold_1.height == (64, 64)

    gold_1.scale = 2.0
    assert gold_1.scale == (2.0, 2.0)
    assert gold_1.width, gold_1.height == (128, 128)

    gold_1.multiply_scale(0.25)
    assert gold_1.scale == (0.5, 0.5)
    assert gold_1.width, gold_1.height == (32, 32)

    # edge case: negative scale values are supported
    gold_1.multiply_scale(-1.0)
    assert gold_1.scale == (-0.5, -0.5)
    assert gold_1.width, gold_1.height == (-32, -32)

    # visual spot check
    character_list = arcade.SpriteList()
    character_sprite = arcade.Sprite(
        ":resources:images/animated_characters/female_person/femalePerson_idle.png",
        scale=CHARACTER_SCALING,
    )
    character_sprite.center_x = 150
    character_sprite.center_y = 150
    character_list.append(character_sprite)

    def on_draw():
        window.clear()
        character_list.draw()

    def update(delta_time):
        character_sprite.add_scale(0.1)

    window.on_draw = on_draw
    window.update = update
    window.test()


def test_render_sprite_remove(window):
    """Render sprites and remove them from the list"""
    CHARACTER_SCALING = 0.5
    global frame
    frame = 0
    window.background_color = arcade.color.AMAZON

    character_list = arcade.SpriteList()

    sprite_1 = arcade.Sprite(
        ":resources:images/animated_characters/female_person/femalePerson_idle.png",
        scale=CHARACTER_SCALING,
    )
    sprite_1.center_x = 150
    sprite_1.center_y = 150
    character_list.append(sprite_1)

    sprite_2 = arcade.Sprite(
        ":resources:images/animated_characters/female_person/femalePerson_idle.png",
        scale=CHARACTER_SCALING,
    )
    sprite_2.center_x = 250
    sprite_2.center_y = 250
    character_list.append(sprite_2)

    sprite_3 = arcade.Sprite(
        ":resources:images/animated_characters/female_person/femalePerson_idle.png",
        scale=CHARACTER_SCALING,
    )
    sprite_3.center_x = 250
    sprite_3.center_y = 250
    character_list.append(sprite_3)

    def on_draw():
        window.clear()
        character_list.draw()

    def update(delta_time):
        global frame
        frame += 1

        if frame == 3:
            sprite_2.remove_from_sprite_lists()

        if frame == 5:
            character_list.remove(sprite_3)

        if frame == 7:
            sprite_2.center_x += 5

        if frame == 9:
            sprite_3.center_x += 5

    window.on_draw = on_draw
    window.on_update = update
    window.test()
