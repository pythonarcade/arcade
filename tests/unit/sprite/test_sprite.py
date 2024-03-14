import pytest as pytest

import arcade

frame_counter = 0


def test_velocity():
    sprite = arcade.SpriteSolidColor(10, 10, color=arcade.color.WHITE)
    sprite.velocity = 1, 2
    assert sprite.velocity == (1, 2)
    assert sprite.change_x == 1
    assert sprite.change_y == 2
    sprite.change_x = 3
    sprite.change_y = 4
    assert sprite.velocity == (3, 4)


def test_sprite(window: arcade.Window):
    CHARACTER_SCALING = 0.5
    window.background_color = arcade.color.AMAZON
    window.clear()
    global frame_counter
    frame_counter = 0

    character_list = arcade.SpriteList()
    character_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", scale=CHARACTER_SCALING)
    character_sprite.center_x = 50
    character_sprite.center_y = 50
    character_sprite.change_x = 2
    character_sprite.change_y = 2
    character_list.append(character_sprite)

    character_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", scale=CHARACTER_SCALING)
    character_sprite.center_x = 150
    character_sprite.center_y = 50
    character_list.append(character_sprite)

    character_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", scale=CHARACTER_SCALING)
    character_sprite.center_x = 200
    character_sprite.center_y = 50
    character_sprite.angle = 45
    character_list.append(character_sprite)

    character_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", scale=CHARACTER_SCALING)
    character_sprite.center_x = 250
    character_sprite.center_y = 50
    character_sprite.angle = 90
    character_list.append(character_sprite)

    character_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", scale= CHARACTER_SCALING)
    character_sprite.center_x = 300
    character_sprite.center_y = 50
    character_sprite.angle = 180
    character_list.append(character_sprite)

    character_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", scale=CHARACTER_SCALING)
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
    sprite = arcade.Sprite(":resources:images/items/coinGold.png", scale=CHARACTER_SCALING)
    sprite.position = (130, 130)
    sprite.angle = 90
    coin_list.append(sprite)

    individual_coin = arcade.Sprite(":resources:images/items/coinGold.png", scale=CHARACTER_SCALING)
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
    window.background_color = arcade.color.AMAZON

    sprite = arcade.Sprite(":resources:images/items/coinGold.png", scale=CHARACTER_SCALING)
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


@pytest.mark.parametrize('not_a_texture', [
    1, "not_a_texture", (1, 2, 3)
])
def test_sprite_texture_setter_raises_type_error_when_given_non_texture(not_a_texture):
    sprite = arcade.Sprite(":resources:images/items/coinGold.png", scale=1.0)
    with pytest.raises(TypeError):
        sprite.texture = not_a_texture


def test_sprite_sizes(window: arcade.Window):
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
    window.background_color = arcade.color.AMAZON

    # ensure normal scaling works correctly
    gold_1 = arcade.Sprite(":resources:/images/items/gold_1.png")
    assert gold_1.scale == (1.0, 1.0)
    assert gold_1.width, gold_1.height == (64, 64)

    gold_1.scale = 2.0
    assert gold_1.scale == (2.0, 2.0)
    assert gold_1.width, gold_1.height == (128, 128)

    gold_1.scale = (x * 0.25 for x in gold_1.scale)
    assert gold_1.scale == (0.5, 0.5)
    assert gold_1.width, gold_1.height == (32, 32)

    # edge case: negative scale values are supported
    gold_1.scale = (x * -1 for x in gold_1.scale)
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
        arcade.start_render()
        character_list.draw()

    def update(delta_time):
        character_sprite.scale = (x + 0.1 for x in gold_1.scale)

    window.on_draw = on_draw
    window.update = update
    window.test()


frame = 0

def test_sprite_removal(window):
    CHARACTER_SCALING = 0.5
    global frame
    frame = 0
    window.background_color = arcade.color.AMAZON

    character_list = arcade.SpriteList()

    sprite_1 = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", scale=CHARACTER_SCALING)
    sprite_1.center_x = 150
    sprite_1.center_y = 150
    character_list.append(sprite_1)

    sprite_2 = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", scale=CHARACTER_SCALING)
    sprite_2.center_x = 250
    sprite_2.center_y = 250
    character_list.append(sprite_2)

    sprite_3 = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", scale=CHARACTER_SCALING)
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


def test_sprite_circle(window):
    # TODO: Improve this
    sprite = arcade.SpriteCircle(50, arcade.color.RED)
    sprite = arcade.SpriteCircle(50, arcade.color.RED, soft=True)


def test_visible():
    sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png")

    # Default values
    assert sprite.alpha == 255
    assert sprite.visible is True

    # initialise alpha value
    sprite.alpha = 100
    assert sprite.alpha == 100

    # Make invisible
    sprite.visible = False
    assert sprite.visible is False
    assert sprite.alpha == 100

    # Make visible again
    sprite.visible = True
    assert sprite.visible is True
    assert sprite.alpha == 100


def test_sprite_rgb_property_basics():
    sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png")

    # Initial multiply tint is white
    assert sprite.rgb == (255, 255, 255)

    # Values which are too short are not allowed
    with pytest.raises(ValueError):
        sprite.rgb = (1,2)
    with pytest.raises(ValueError):
        sprite.rgb = (0,)

    # Nor are values which are too long
    with pytest.raises(ValueError):
        sprite.rgb = (100,100,100,100,100)

    # Test color setting + .rgb report when .visible == True
    sprite.rgb = (1, 3, 5, 7)
    assert sprite.color.r == 1
    assert sprite.color.g == 3
    assert sprite.color.b == 5
    assert sprite.rgb[0] == 1
    assert sprite.rgb[1] == 3
    assert sprite.rgb[2] == 5

    # Test alpha preservation
    assert sprite.color.a == 255
    assert sprite.alpha == 255

    # Test .rgb sets rgb chanels when visible == False as with .color,
    # but also still preserves original alpha values.
    sprite.visible = False
    sprite.color = (9, 11, 13, 15)
    sprite.rgb = (17, 21, 23, 25)

    # Check the color channels
    assert sprite.color.r == 17
    assert sprite.color.g == 21
    assert sprite.color.b == 23
    assert sprite.rgb[0] == 17
    assert sprite.rgb[1] == 21
    assert sprite.rgb[2] == 23

    # Alpha preserved?
    assert sprite.color.a == 15
    assert sprite.alpha == 15


def test_sprite_scale_xy(window):
    sprite = arcade.SpriteSolidColor(20, 20, color=arcade.color.WHITE)

    # setting vector equivalent of previous scale doesn't change values
    sprite.scale = 1.0
    sprite.scale = (1.0, 1.0)
    assert sprite.scale == (1.0, 1.0)
    assert sprite.width, sprite.height == (20, 20)

    # setting scale_xy to identical values in each channel works
    sprite.scale = 2.0, 2.0
    assert sprite.scale == (2.0, 2.0)
    assert sprite.width, sprite.height == (40, 40)

    # setting scale_xy with x < y scale works correctly
    sprite.scale = 1.0, 4.0
    assert sprite.scale == (1.0, 4.0)
    assert sprite.scale_x == 1.0
    assert sprite.scale_y == 4.0
    assert sprite.width, sprite.height == (20, 80)

    # setting scale_xy with x > y scale works correctly
    sprite.scale = 5.0, 3.0
    assert sprite.scale == (5.0, 3.0)
    assert sprite.scale_x == 5.0
    assert sprite.scale_y == 3.0
    assert sprite.width, sprite.height == (100, 60)

    # edge case: setting scale_xy with x < 0 works correctly
    sprite.scale = -1.0, 1.0
    assert sprite.scale == (-1.0, 1.0)
    assert sprite.width == -20
    assert sprite.height == 20

    # edge case: setting scale_xy with y < 0 works correctly
    sprite.scale = (1.0, -1.0)
    assert sprite.scale_x == 1.0
    assert sprite.scale_y == -1.0
    assert sprite.width == 20
    assert sprite.height == -20

    # edge case: setting scale_xy with x < 0, y < 0 works correctly
    sprite.scale = (-1.0, -1.0)
    assert sprite.scale_x == -1.0
    assert sprite.scale_y == -1.0
    assert sprite.width == -20
    assert sprite.width == -20


def test_sprite_scale_resets_mismatched_xy_settings(window):
    sprite = arcade.SpriteSolidColor(20, 20, color=arcade.color.WHITE)

    # check if x dimension is properly reset
    sprite.scale = 3.0, 2.0
    sprite.scale = 2.0
    assert sprite.scale == (2.0, 2.0)
    assert sprite.width == 40
    assert sprite.height == 40

    # check if y dimension is properly reset
    sprite.scale = 5.0, 3.0
    sprite.scale = 5.0
    assert sprite.scale_x == 5.0
    assert sprite.scale == (5.0, 5.0)
    assert sprite.width == 100
    assert sprite.height == 100

    # check if both dimensions properly reset
    sprite.scale = 0.5, 4.0
    sprite.scale = 1.0
    assert sprite.scale_x == 1.0
    assert sprite.scale == (1.0, 1.0)
    assert sprite.width == 20
    assert sprite.height == 20

    # edge case: setting negative values works
    sprite.scale = 0.5, 4.0
    sprite.scale = -1.0
    assert sprite.scale_x == -1.0
    assert sprite.scale == (-1.0, -1.0)
    assert sprite.width == -20
    assert sprite.height == -20

    # edge case: x scale < 0 is reset to positive
    sprite.scale = -1.0, 1.0
    sprite.scale = 2.0
    assert sprite.scale == (2.0, 2.0)
    assert sprite.width == 40
    assert sprite.height == 40

    # edge case: y scale < 0 is reset to positive
    sprite.scale = 1.0, -1.0
    sprite.scale = 2.0
    assert sprite.scale == (2.0, 2.0)
    assert sprite.width == 40
    assert sprite.height == 40

    # edge case: x < 0, y < 0 is reset to positive
    sprite.scale = -1.0, -1.0
    sprite.scale = 2.0
    assert sprite.scale == (2.0, 2.0)
    assert sprite.width == 40
    assert sprite.height == 40


def test_rescale_relative_to_point(window):
    window_center = window.width // 2, window.height // 2
    window_center_x, window_center_y = window_center

    def sprite_64x64_at_position(x, y):
        return arcade.Sprite(
            ":resources:images/items/gold_1.png",
            center_x=x,
            center_y=y,
        )

    # case:
    #  1. sprite initial scale_xy == (1.0, 1.0) / scale == 1.0
    #  2. point is the origin in the lower left
    #  3. factor == 3.31
    # expected:
    #  1. sprite is 3.31 times further away from origin to upper right
    #  2. sprite is now 3.31 times larger
    sprite_1 = sprite_64x64_at_position(
        window_center_x + 50,
        window_center_y - 50
    )
    sprite_1.rescale_relative_to_point((0, 0), 3.31)
    assert sprite_1.scale == (3.31, 3.31)
    assert sprite_1.center_x == (window_center_x + 50) * 3.31
    assert sprite_1.center_y == (window_center_y - 50) * 3.31
    assert sprite_1.width == 64 * 3.31
    assert sprite_1.height == 64 * 3.31

    # case:
    #  1. sprite is offset from center
    #  2. initial scale_xy values are not equal
    #  3. factor == 2.0
    # result:
    #  1. sprite distance doubled
    #  2. sprite scale doubled
    sprite_2 = sprite_64x64_at_position(
        window_center_x + 10,
        window_center_y + 10
    )
    sprite_2.scale = (2.0, 1.0)
    sprite_2.rescale_relative_to_point(window_center, 2.0)
    assert sprite_2.scale == (4.0, 2.0)
    assert sprite_2.center_x == window_center_x + 20
    assert sprite_2.center_y == window_center_y + 20
    assert sprite_2.width == 256
    assert sprite_2.height == 128

    # case:
    #  1. sprite is offset from center
    #  2. initial scale_xy values are not equal
    #  3. factor == 3.0
    # result:
    #  1. sprite distance tripled
    #  2. sprite scale tripled
    sprite_3 = sprite_64x64_at_position(
        window_center_x - 10,
        window_center_y - 10
    )
    sprite_3.scale = (0.5, 1.5)
    sprite_3.rescale_relative_to_point(window_center, 3.0)
    assert sprite_3.scale == (1.5, 4.5)
    assert sprite_3.center_x == window_center_x - 30
    assert sprite_3.center_y == window_center_y - 30
    assert sprite_3.width == 96
    assert sprite_3.height == 288

    # edge case: point == sprite center, factor > 1
    # expected: sprite does not move, but scale and dimensions change
    sprite_4 = sprite_64x64_at_position(*window_center)
    sprite_4.rescale_relative_to_point(sprite_4.position, 2.0)
    assert sprite_4.scale == (2.0, 2.0)
    assert sprite_4.center_x == window_center_x
    assert sprite_4.center_y == window_center_y
    assert sprite_4.width == 128
    assert sprite_4.height == 128

    # edge case: point == sprite center, negative factor
    # expected : sprite doesn't move, but scale data doubled & negative
    sprite_5 = sprite_64x64_at_position(*window_center)
    sprite_5.rescale_relative_to_point(sprite_5.position, -2.0)
    assert sprite_5.scale == (-2.0, -2.0)
    assert sprite_5.center_x == window_center_x
    assert sprite_5.center_y == window_center_y
    assert sprite_5.width == -128
    assert sprite_5.height == -128

    # edge case: point != sprite center, factor == 1.0
    # expected : no movement or size change occurs
    sprite_6 = sprite_64x64_at_position(
        window_center_x - 81,
        window_center_y + 81
    )
    sprite_6.rescale_relative_to_point((50, 40), 1.0)
    assert sprite_6.scale == (1.0, 1.0)
    assert sprite_6.center_x == window_center_x - 81
    assert sprite_6.center_y == window_center_y + 81
    assert sprite_6.width == 64
    assert sprite_6.height == 64

    # edge case: point != sprite center, factor == 1.0
    # expected : no movement or size change occurs
    sprite_7 = sprite_64x64_at_position(
        window_center_x - 81,
        window_center_y + 81
    )
    sprite_7.rescale_relative_to_point((50, 40), 1.0)
    assert sprite_7.scale == (1.0, 1.0)
    assert sprite_7.center_x == window_center_x - 81
    assert sprite_7.center_y == window_center_y + 81
    assert sprite_7.width == 64
    assert sprite_7.height == 64

    # edge case: point != sprite center, negative factor
    # expected :
    #  1. sprite teleports to opposite side of point
    #  2. sprite has negative versions of scale data
    sprite_8 = sprite_64x64_at_position(
        window_center_x - 81,
        window_center_y + 81
    )
    sprite_8.rescale_relative_to_point(window_center, -1.0)
    assert sprite_8.scale == (-1.0, -1.0)
    assert sprite_8.center_x == window_center_x + 81
    assert sprite_8.center_y == window_center_y - 81
    assert sprite_8.width == -64
    assert sprite_8.height == -64


def test_rescale_xy_relative_to_point(window):
    window_center = window.width // 2, window.height // 2
    window_center_x, window_center_y = window_center

    def sprite_64x64_at_position(x, y):
        return arcade.Sprite(
            ":resources:images/items/gold_1.png",
            center_x=x, center_y=y
        )

    # sprite with initial _scale[0] == _scale[1] works with identical scale
    sprite_1 = sprite_64x64_at_position(
        window_center_x + 50,
        window_center_y - 50
    )
    sprite_1.rescale_xy_relative_to_point((0, 0), (3.31, 3.31))
    assert sprite_1.scale == (3.31, 3.31)
    assert sprite_1.center_x == (window_center_x + 50) * 3.31
    assert sprite_1.center_y == (window_center_y - 50) * 3.31
    assert sprite_1.width == 64 * 3.31
    assert sprite_1.height == 64 * 3.31

    # sprite with x scale > y scale works correctly
    sprite_2 = sprite_64x64_at_position(
        window_center_x + 10,
        window_center_y + 10
    )
    sprite_2.scale = (2.0, 1.0)
    sprite_2.rescale_xy_relative_to_point(window_center, (2.0, 2.0))
    assert sprite_2.scale == (4.0, 2.0)
    assert sprite_2.center_x == window_center_x + 20
    assert sprite_2.center_y == window_center_y + 20
    assert sprite_2.width == 256
    assert sprite_2.height == 128

    # sprite with y scale > x scale works correctly
    sprite_3 = sprite_64x64_at_position(
        window_center_x - 10,
        window_center_y - 10
    )
    sprite_3.scale = (0.5, 1.5)
    sprite_3.rescale_xy_relative_to_point(window_center, (3.0, 3.0))
    assert sprite_3.scale == (1.5, 4.5)
    assert sprite_3.center_x == window_center_x - 30
    assert sprite_3.center_y == window_center_y - 30
    assert sprite_3.width == 96
    assert sprite_3.height == 288

    # edge case: point == sprite center, factor > 1
    # expected: sprite does not move, but scale and dimensions change
    sprite_4 = sprite_64x64_at_position(*window_center)
    sprite_4.rescale_xy_relative_to_point(sprite_4.position, (2.0, 2.0))
    assert sprite_4.scale == (2.0, 2.0)
    assert sprite_4.center_x == window_center_x
    assert sprite_4.center_y == window_center_y
    assert sprite_4.width == 128
    assert sprite_4.height == 128

    # edge case: point != sprite center, factor == 1.0
    # expected : no movement or size change occurs
    sprite_5 = sprite_64x64_at_position(
        window_center_x - 81,
        window_center_y + 81
    )
    sprite_5.rescale_xy_relative_to_point((50, 40), (1.0, 1.0))
    assert sprite_5.scale == (1.0, 1.0)
    assert sprite_5.center_x == window_center_x - 81
    assert sprite_5.center_y == window_center_y + 81
    assert sprite_5.width == 64
    assert sprite_5.height == 64

    # edge case: point == sprite center, negative factor
    # expected : sprite doesn't move, but scale, width, & height < 0
    sprite_6 = sprite_64x64_at_position(*window_center)
    sprite_6.rescale_xy_relative_to_point(sprite_6.position, (-2.0, -2.0))
    assert sprite_6.scale == (-2.0, -2.0)
    assert sprite_6.center_x == window_center_x
    assert sprite_6.center_y == window_center_y
    assert sprite_6.width == -128
    assert sprite_6.height == -128

    # edge case: point != sprite center, factor == 1.0
    # expected : no movement or size change occurs
    sprite_7 = sprite_64x64_at_position(
        window_center_x - 81,
        window_center_y + 81
    )
    sprite_7.rescale_xy_relative_to_point((50, 40), (1.0, 1.0))
    assert sprite_7.scale == (1.0, 1.0)
    assert sprite_7.center_x == window_center_x - 81
    assert sprite_7.center_y == window_center_y + 81
    assert sprite_7.width == 64
    assert sprite_7.height == 64


def test_strafe(window):
    sprite = arcade.SpriteSolidColor(10, 10, color=arcade.color.WHITE)
    assert sprite.position == (0, 0)

    sprite.forward(2)
    assert sprite.position == (0, 2)

    sprite.reverse(2)
    assert sprite.position == (0, 0)

    sprite.strafe(2)
    pos = round(sprite.center_x, 2), round(sprite.center_y, 2)
    assert pos == (2, 0)

    sprite.strafe(-2)
    pos = round(sprite.center_x, 2), round(sprite.center_y, 2)
    assert pos == (0, 0)

    sprite.angle = 90
    sprite.strafe(2)
    pos = round(sprite.center_x, 2), round(sprite.center_y, 2)
    assert pos == (0.0, -2.0)
