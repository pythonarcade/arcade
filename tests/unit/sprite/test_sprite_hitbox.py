import arcade
from arcade import hitbox


def test_1():
    # setup
    my_sprite = arcade.Sprite(arcade.make_soft_square_texture(20, arcade.color.RED, 0, 255))
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


SQUARE = ((-10, -10), (-10, 10), (10, 10), (10, -10))


def _rounded(points):
    return [(round(x, 6), round(y, 6)) for x, y in points]


def test_set_hit_box_matches_sprite():
    """A new hit box takes the sprite's position, scale and angle right away"""
    sprite = arcade.SpriteSolidColor(20, 20, center_x=100, center_y=50)
    sprite.scale = 2
    sprite.angle = 90
    sprite.hit_box = hitbox.HitBox(SQUARE)

    assert sprite.hit_box.position == (100, 50)
    assert sprite.hit_box.scale == (2, 2)
    assert sprite.hit_box.angle == 90
    # Clockwise rotation by 90 degrees, then scaled by 2 and moved
    assert _rounded(sprite.hit_box.get_adjusted_points()) == [
        (80, 70), (120, 70), (120, 30), (80, 30)
    ]  # fmt: skip


def test_set_rotatable_hit_box_matches_sprite():
    """A RotatableHitBox's own position, scale and angle are replaced too"""
    sprite = arcade.SpriteSolidColor(20, 20, center_x=100, center_y=50)
    sprite.scale = 0.5
    sprite.hit_box = hitbox.RotatableHitBox(SQUARE, position=(7, 7), angle=30, scale=(3, 3))
    assert sprite.hit_box.position == (100, 50)
    assert sprite.hit_box.scale == (0.5, 0.5)
    assert sprite.hit_box.angle == 0
    assert _rounded(sprite.hit_box.get_adjusted_points()) == [
        (95, 45), (95, 55), (105, 55), (105, 45)
    ]  # fmt: skip


def test_set_hit_box_follows_sprite_afterwards():
    sprite = arcade.SpriteSolidColor(20, 20, center_x=100, center_y=50)
    sprite.hit_box = hitbox.HitBox(SQUARE)
    sprite.position = 10, 20
    sprite.scale = 3
    assert _rounded(sprite.hit_box.get_adjusted_points()) == [
        (-20, -10), (-20, 50), (40, 50), (40, -10)
    ]  # fmt: skip


def test_set_hit_box_collides_right_away():
    """The hit box used to stay at (0, 0) until the sprite moved, so it hit nothing"""
    sprite = arcade.SpriteSolidColor(20, 20, center_x=100, center_y=100)
    sprite.hit_box = hitbox.HitBox(SQUARE)
    other = arcade.SpriteSolidColor(20, 20, center_x=110, center_y=100)
    assert arcade.check_for_collision(sprite, other)


def test_set_hit_box_updates_spatial_hash():
    """A bigger hit box is found by a spatial hash without moving the sprite"""
    sprite_list = arcade.SpriteList(use_spatial_hash=True)
    sprite = arcade.SpriteSolidColor(20, 20, center_x=100, center_y=100)
    sprite_list.append(sprite)
    sprite.hit_box = hitbox.HitBox([(-200, -200), (200, -200), (200, 200), (-200, 200)])
    far_away = arcade.SpriteSolidColor(10, 10, center_x=250, center_y=250)
    assert arcade.check_for_collision_with_list(far_away, sprite_list) == [sprite]
