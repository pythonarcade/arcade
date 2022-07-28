import arcade

frame_counter = 0


def test_sprite(window: arcade.Window):
    CHARACTER_SCALING = 0.5
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


def test_sprite_2(window):
    CHARACTER_SCALING = 1.0
    arcade.set_background_color(arcade.color.AMAZON)

    sprite = arcade.Sprite(":resources:images/items/coinGold.png", CHARACTER_SCALING)
    sprite.center_x = 50
    sprite.center_y = 50

    sprite_list = arcade.SpriteList()
    sprite_list.append(sprite)

    def on_draw():
        arcade.start_render()
        assert arcade.get_pixel(50, 50) == (59, 122, 87)
        sprite.draw()
        assert arcade.get_pixel(50, 50) == (255, 204, 0)

    window.on_draw = on_draw
    window.test(2)


def test_sprite_sizes(window: arcade.Window):
    SIZE = 50
    SPACING = SIZE * 2
    ROW_SPACING = 100
    arcade.set_background_color(arcade.color.BLACK)

    character_list = arcade.SpriteList()

    for i in range(7):
        my_width = SIZE
        my_height = SIZE + i * 3
        my_color = (i * 40, 0, 255)
        center_x = SPACING + (i * SPACING)
        center_y = ROW_SPACING
        character_sprite = arcade.SpriteSolidColor(my_width, my_height, my_color)
        character_sprite.center_x = center_x
        character_sprite.center_y = center_y
        character_list.append(character_sprite)

    for i in range(7):
        my_width = SIZE + i * 3
        my_height = SIZE
        my_color = (0, i * 40, 255)
        center_x = SPACING + (i * SPACING)
        center_y = ROW_SPACING * 2
        character_sprite = arcade.SpriteSolidColor(my_width, my_height, my_color)
        character_sprite.center_x = center_x
        character_sprite.center_y = center_y
        character_list.append(character_sprite)

    def on_draw():
        arcade.start_render()
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


def test_sprite_scale(window):
    CHARACTER_SCALING = 0.5
    arcade.set_background_color(arcade.color.AMAZON)

    character_list = arcade.SpriteList()
    character_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
    character_sprite.center_x = 150
    character_sprite.center_y = 150
    character_list.append(character_sprite)

    def on_draw():
        arcade.start_render()
        character_list.draw()

    def update(delta_time):
        character_sprite.scale += 0.1

    window.on_draw = on_draw
    window.update = update
    window.test()
    arcade.cleanup_texture_cache()


frame = 0

def test_sprite_removal(window):
    CHARACTER_SCALING = 0.5
    global frame
    frame = 0
    arcade.set_background_color(arcade.color.AMAZON)

    character_list = arcade.SpriteList()

    sprite_1 = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
    sprite_1.center_x = 150
    sprite_1.center_y = 150
    character_list.append(sprite_1)

    sprite_2 = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
    sprite_2.center_x = 250
    sprite_2.center_y = 250
    character_list.append(sprite_2)

    sprite_3 = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
    sprite_3.center_x = 250
    sprite_3.center_y = 250
    character_list.append(sprite_3)


    def on_draw():
        arcade.start_render()
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
    window.update = update
    window.test()
    arcade.cleanup_texture_cache()


def test_visible():
    sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png")

    # Default values
    assert sprite.alpha == 255
    assert sprite.visible is True

    # Make invisible
    sprite.visible = False
    assert sprite.visible is False
    assert sprite.alpha == 0

    # Make visible again
    sprite.visible = True
    assert sprite.visible is True
    assert sprite.alpha == 255


def test_sprite_scale_xy(window):
    sprite = arcade.SpriteSolidColor(20, 20, arcade.color.WHITE)
    assert sprite.scale == 1.0
    assert sprite.scale_xy == (1.0, 1.0)
    sprite.scale = 2.0
    assert sprite.scale == 2.0
    assert sprite.scale_xy == (2.0, 2.0)
    sprite.scale_xy = 2.0, 4.0
    assert sprite.scale_xy == (2.0, 4.0)
    assert sprite.scale == 2.0
