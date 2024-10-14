import arcade
from arcade import hitbox


def test_1():
    # setup
    my_sprite = arcade.Sprite(
        arcade.make_soft_square_texture(20, arcade.color.RED, 0, 255)
    )
    hit_box = arcade.hitbox.HitBox(((-10, -10), (-10, 10), (10, 10), (10, -10)))
    my_sprite.hit_box = hit_box
    my_sprite.scale = 1.0
    my_sprite.angle = 0
    my_sprite.center_x = 100
    my_sprite.center_y = 100

    print()
    hitbox = my_sprite.hit_box.get_adjusted_points()
    print(f"Hitbox: {my_sprite.scale} -> {my_sprite.hit_box.points} -> {hitbox}")
    assert hitbox == [(90.0, 90.0), (90.0, 110.0), (110.0, 110.0), (110.0, 90.0)]

    my_sprite.scale = 0.5, 0.5
    hitbox = my_sprite.hit_box.get_adjusted_points()
    print(f"Hitbox: {my_sprite.scale} -> {my_sprite.hit_box.points} -> {hitbox}")
    assert hitbox == [(95.0, 95.0), (95.0, 105.0), (105.0, 105.0), (105.0, 95.0)]

    my_sprite.scale = 1.0
    hitbox = my_sprite.hit_box.get_adjusted_points()
    print(f"Hitbox: {my_sprite.scale} -> {my_sprite.hit_box.points} -> {hitbox}")
    assert hitbox == [(90.0, 90.0), (90.0, 110.0), (110.0, 110.0), (110.0, 90.0)]

    my_sprite.scale = 2.0
    hitbox = my_sprite.hit_box.get_adjusted_points()
    print(f"Hitbox: {my_sprite.scale} -> {my_sprite.hit_box.points} -> {hitbox}")
    assert hitbox == [(80.0, 80.0), (80.0, 120.0), (120.0, 120.0), (120.0, 80.0)]

    my_sprite.scale = 2.0
    hitbox = my_sprite.hit_box.get_adjusted_points()
    print(f"Hitbox: {my_sprite.scale} -> {my_sprite.hit_box.points} -> {hitbox}")
    assert hitbox == [(80.0, 80.0), (80.0, 120.0), (120.0, 120.0), (120.0, 80.0)]


def test_2():
    height = 2
    width = 2
    wall = arcade.SpriteSolidColor(width, height, color=arcade.color.RED)
    wall.position = 0, 0

    assert wall.height == height
    assert wall.width == width
    assert wall.top == height / 2
    assert wall.bottom == -height / 2
    assert wall.left == -width / 2
    assert wall.right == width / 2
    hit_box = wall.hit_box.points
    assert hit_box[0] == (-width / 2, -height / 2)
    assert hit_box[1] == (width / 2, -height / 2)
    assert hit_box[2] == (width / 2, height / 2)
    assert hit_box[3] == (-width / 2, height / 2)

    height = 128
    width = 128
    wall = arcade.SpriteSolidColor(width, height, color=arcade.color.RED)
    wall.position = 0, 0

    assert wall.height == height
    assert wall.width == width
    assert wall.top == height / 2
    assert wall.bottom == -height / 2
    assert wall.left == -width / 2
    assert wall.right == width / 2
    hit_box = wall.hit_box.points
    assert hit_box[0] == (-width / 2, -height / 2)
    assert hit_box[1] == (width / 2, -height / 2)
    assert hit_box[2] == (width / 2, height / 2)
    assert hit_box[3] == (-width / 2, height / 2)

    height = 128
    width = 128
    wall = arcade.Sprite(":resources:images/tiles/dirtCenter.png")
    wall.position = 0, 0

    assert wall.height == height
    assert wall.width == width
    assert wall.top == height / 2
    assert wall.bottom == -height / 2
    assert wall.left == -width / 2
    assert wall.right == width / 2
    hit_box = wall.hit_box.points
    assert hit_box[0] == (-width / 2, -height / 2)
    assert hit_box[1] == (width / 2, -height / 2)
    assert hit_box[2] == (width / 2, height / 2)
    assert hit_box[3] == (-width / 2, height / 2)

    texture = arcade.load_texture(
        ":resources:images/items/coinGold.png", hit_box_algorithm=hitbox.algo_detailed
    )
    wall = arcade.Sprite(texture)
    wall.position = 0, 0

    hit_box = list(wall.hit_box.points)
    assert hit_box == [
        (-32.0, 7.0),
        (-17.0, 28.0),
        (7.0, 32.0),
        (29.0, 15.0),
        (32.0, -7.0),
        (17.0, -28.0),
        (-8.0, -32.0),
        (-28.0, -17.0),
    ]
