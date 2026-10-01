import random

import pytest

import arcade


def test_sprites_at_point():
    coin_list = arcade.SpriteList()
    sprite = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    # an adjacent sprite with the same level horizontal bottom edge
    sprite2 = arcade.SpriteSolidColor(50, 50, center_x=50, center_y=0, color=arcade.csscolor.RED)

    coin_list.append(sprite)
    coin_list.append(sprite2)

    sprite_list = arcade.get_sprites_at_point((0, 0), coin_list)
    assert len(sprite_list) == 1

    sprite_list = arcade.get_sprites_at_point((50, 0), coin_list)
    assert len(sprite_list) == 1

    sprite_list = arcade.get_sprites_at_point((0, -25), coin_list)
    assert len(sprite_list) == 1

    sprite.position = (130, 130)

    sprite_list = arcade.get_sprites_at_point((0, 0), coin_list)
    assert len(sprite_list) == 0

    sprite_list = arcade.get_sprites_at_point((140, 130), coin_list)
    assert len(sprite_list) == 1

    sprite.angle = 90

    sprite_list = arcade.get_sprites_at_point((0, 0), coin_list)
    assert len(sprite_list) == 0

    sprite_list = arcade.get_sprites_at_point((140, 130), coin_list)
    assert len(sprite_list) == 1


def test_sprite_collides_with_point():
    sprite = arcade.SpriteSolidColor(32, 32, color=arcade.csscolor.RED)
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
    point = (0, 2)
    assert sprite.collides_with_point(point) is False
    point = (2, 0)
    assert sprite.collides_with_point(point) is False
    point = (2, 2)
    assert sprite.collides_with_point(point) is False
    point = (-2, -2)
    assert sprite.collides_with_point(point) is False
    point = (-2, 0)
    assert sprite.collides_with_point(point) is False


def test_sprite_collides_with_sprite():
    sprite_one = arcade.SpriteSolidColor(32, 32, color=arcade.csscolor.RED)
    sprite_one.width = 10
    sprite_one.height = 10

    sprite_two = arcade.SpriteSolidColor(32, 32, color=arcade.csscolor.RED)
    sprite_two.width = 10
    sprite_two.height = 10

    sprite_three = arcade.SpriteSolidColor(32, 32, color=arcade.csscolor.RED)
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
        coin = arcade.SpriteSolidColor(32, 32, color=arcade.csscolor.RED)
        coin.position = x, 0
        coin.width = 10
        coin.height = 10
        coins.append(coin)

    player = arcade.SpriteSolidColor(32, 32, color=arcade.csscolor.RED)
    player.position = 100, 100
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


def test_get_closest_sprite(window):
    a = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    b = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    c = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)

    a.position = 0, 0
    b.position = 50, 50
    c.position = 100, 0

    sl = arcade.SpriteList()
    sl.extend((c, b))

    # Empty spritelist
    assert arcade.get_closest_sprite(a, arcade.SpriteList()) is None

    # Default closest sprite
    sprite, distance = arcade.get_closest_sprite(a, sl)
    assert sprite == b
    assert distance == pytest.approx(70.710678)


def test_check_for_collision(window):
    a = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    b = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    sp = arcade.SpriteList()

    # Check various incorrect arguments
    with pytest.raises(TypeError):
        arcade.check_for_collision("moo", b)
    with pytest.raises(TypeError):
        arcade.check_for_collision(a, "moo")
    with pytest.raises(TypeError):
        arcade.check_for_collision(a, sp)

    assert arcade.check_for_collision(a, b) is True
    b.position = 100, 0
    assert arcade.check_for_collision(a, b) is False


@pytest.mark.parametrize(
    "scale_a, scale_b",
    [
        ((-1, -1), (1, 1)),
        ((1, 1), (-1, -1)),
        ((-1, -1), (-1, -1)),
        ((-1, 1), (1, -1)),
        ((-2, -2), (0.5, 0.5)),
    ],
)
def test_check_for_collision_negative_scale(window, scale_a, scale_b):
    """Flipping a sprite with a negative scale must not affect collisions."""
    a = arcade.SpriteSolidColor(64, 64, color=arcade.csscolor.RED)
    b = arcade.SpriteSolidColor(64, 64, center_x=20, color=arcade.csscolor.RED)
    a.scale = scale_a
    b.scale = scale_b
    assert arcade.check_for_collision(a, b) is True
    assert arcade.check_for_collision(b, a) is True

    b.position = 500, 0
    assert arcade.check_for_collision(a, b) is False


def test_check_for_collision_hit_box_bigger_than_texture(window):
    """A custom hit box bigger than the texture must still collide."""
    a = arcade.SpriteSolidColor(32, 32, color=arcade.csscolor.RED)
    # Like a melee reach area around the sprite
    a.hit_box = arcade.hitbox.HitBox([(-50, -50), (50, -50), (50, 50), (-50, 50)])
    # Overlaps the hit box, but is too far away to touch the texture
    b = arcade.SpriteSolidColor(32, 32, center_x=60, color=arcade.csscolor.RED)
    assert arcade.check_for_collision(a, b) is True
    assert arcade.check_for_collision(b, a) is True

    sprite_list = arcade.SpriteList()
    sprite_list.append(b)
    assert arcade.check_for_collision_with_list(a, sprite_list, method=3) == [b]
    sprite_list.enable_spatial_hashing()
    assert arcade.check_for_collision_with_list(a, sprite_list, method=1) == [b]

    # Still found when rotated, scaled, or flipped
    a.angle = 45
    b.position = 70, 0
    assert arcade.check_for_collision(a, b) is True
    a.scale = (-1.5, 1.5)
    b.position = 90, 0
    assert arcade.check_for_collision(a, b) is True

    # And not when it really is out of reach
    b.position = 200, 0
    assert arcade.check_for_collision(a, b) is False


def test_collision_method_values():
    """CollisionMethod is an IntEnum, so the old numbers still work"""
    assert arcade.CollisionMethod.AUTO == 0
    assert arcade.CollisionMethod.SPATIAL == 1
    assert arcade.CollisionMethod.GPU == 2
    assert arcade.CollisionMethod.SIMPLE == 3
    assert arcade.CollisionMethod(2) is arcade.CollisionMethod.GPU


# (method, spatial hash, sprite count, webgl, expected path)
COLLISION_METHOD_PATHS = [
    (arcade.CollisionMethod.AUTO, True, 10, False, "spatial"),
    (arcade.CollisionMethod.AUTO, False, 10, False, "simple"),
    (arcade.CollisionMethod.AUTO, False, 1501, False, "gpu"),
    (arcade.CollisionMethod.SPATIAL, True, 10, False, "spatial"),
    # Without a spatial hash, SPATIAL chooses the same way as AUTO
    (arcade.CollisionMethod.SPATIAL, False, 10, False, "simple"),
    (arcade.CollisionMethod.SPATIAL, False, 1501, False, "gpu"),
    (arcade.CollisionMethod.SPATIAL, False, 1501, True, "simple"),
    (arcade.CollisionMethod.GPU, True, 10, False, "gpu"),
    (arcade.CollisionMethod.GPU, False, 10, False, "gpu"),
    (arcade.CollisionMethod.SIMPLE, True, 10, False, "simple"),
    (arcade.CollisionMethod.SIMPLE, False, 1501, False, "simple"),
    (arcade.CollisionMethod.GPU, False, 10, True, "simple"),
    (arcade.CollisionMethod.AUTO, False, 1501, True, "simple"),
    (arcade.CollisionMethod.AUTO, True, 1501, True, "spatial"),
]


@pytest.mark.parametrize("use_int", [False, True], ids=["enum", "int"])
@pytest.mark.parametrize("method, spatial, count, webgl, expected", COLLISION_METHOD_PATHS)
def test_collision_method_paths(
    window, monkeypatch, use_int, method, spatial, count, webgl, expected
):
    """Each method finds the sprites to check the expected way"""
    from arcade.sprite_list import collision

    sprite = arcade.SpriteSolidColor(10, 10)
    sprite_list = arcade.SpriteList(use_spatial_hash=spatial)
    for i in range(count):
        sprite_list.append(arcade.SpriteSolidColor(10, 10, center_x=i * 20))

    calls = []
    monkeypatch.setattr(collision, "_get_nearby_sprites", lambda *args: calls.append("gpu") or [])
    if spatial:
        near = sprite_list.spatial_hash.get_sprites_near_sprite
        monkeypatch.setattr(
            sprite_list.spatial_hash,
            "get_sprites_near_sprite",
            lambda s: calls.append("spatial") or near(s),
        )
    if webgl:

        class FakeWindow:
            class ctx:
                _gl_api = "webgl"

        monkeypatch.setattr(collision, "get_window", lambda: FakeWindow)

    m = int(method) if use_int else method
    hits = arcade.check_for_collision_with_list(sprite, sprite_list, method=m)
    assert calls == ([] if expected == "simple" else [expected])
    if expected != "gpu":
        # The sprite at the origin overlaps the first sprite in the list
        assert hits == [sprite_list[0]]

    calls.clear()
    arcade.check_for_collision_with_lists(sprite, [sprite_list], method=m)
    assert calls == ([] if expected == "simple" else [expected])


def test_check_for_collision_with_lists_no_duplicates(window):
    """A sprite in more than one of the lists is only returned once"""
    sprite = arcade.SpriteSolidColor(10, 10)
    shared = arcade.SpriteSolidColor(10, 10, center_x=5)
    only_a = arcade.SpriteSolidColor(10, 10, center_x=-5)
    only_b = arcade.SpriteSolidColor(10, 10, center_y=5)
    list_a = arcade.SpriteList()
    list_a.extend([only_a, shared])
    list_b = arcade.SpriteList()
    list_b.extend([shared, only_b])

    # In the order first found
    assert arcade.check_for_collision_with_lists(sprite, [list_a, list_b]) == [
        only_a,
        shared,
        only_b,
    ]
    assert arcade.check_for_collision_with_lists(sprite, [list_b, list_a]) == [
        shared,
        only_b,
        only_a,
    ]
    # The same list twice, and lists from a generator
    assert arcade.check_for_collision_with_lists(sprite, [list_a, list_a]) == [only_a, shared]
    assert arcade.check_for_collision_with_lists(sprite, (sl for sl in [list_a, list_b])) == [
        only_a,
        shared,
        only_b,
    ]

    # With a spatial hash. It finds sprites in no particular order.
    hashed_b = arcade.SpriteList(use_spatial_hash=True)
    hashed_b.extend([shared, only_b])
    hits = arcade.check_for_collision_with_lists(sprite, [list_a, hashed_b])
    assert len(hits) == 3
    assert set(hits) == {only_a, shared, only_b}


def test_touching_edges(window):
    """Touching hit boxes don't collide, but a point on an edge counts"""
    a = arcade.SpriteSolidColor(10, 10)
    b = arcade.SpriteSolidColor(10, 10, center_x=10)  # Shares a's right edge
    c = arcade.SpriteSolidColor(10, 10, center_x=10, center_y=10)  # Shares a corner
    sprite_list = arcade.SpriteList()
    sprite_list.append(a)

    assert arcade.check_for_collision(a, b) is False
    assert arcade.check_for_collision(a, c) is False
    assert a.collides_with_sprite(b) is False
    assert arcade.check_for_collision_with_list(b, sprite_list) == []
    assert arcade.get_sprites_in_rect(arcade.LRBT(5, 8, -2, 2), sprite_list) == []

    assert a.collides_with_point((5, 0)) is True
    assert a.collides_with_point((5, 5)) is True
    assert arcade.get_sprites_at_point((5, 0), sprite_list) == [a]


@pytest.mark.parametrize("method", list(arcade.CollisionMethod))
@pytest.mark.parametrize("spatial", [False, True])
def test_has_collision_with_list(window, method, spatial):
    """has_collision_with_list matches whether check_for_collision_with_list finds anything"""
    sprite = arcade.SpriteSolidColor(10, 10)
    sprite_list = arcade.SpriteList(use_spatial_hash=spatial)
    for x in (100, 200):
        sprite_list.append(arcade.SpriteSolidColor(10, 10, center_x=x))
    # A sprite never collides with itself
    sprite_list.append(sprite)

    assert arcade.has_collision_with_list(sprite, sprite_list, method=method) is False
    assert arcade.check_for_collision_with_list(sprite, sprite_list, method=method) == []

    sprite.center_x = 195
    assert arcade.has_collision_with_list(sprite, sprite_list, method=method) is True
    assert arcade.check_for_collision_with_list(sprite, sprite_list, method=method) != []

    # Touching edges don't count, the same as check_for_collision
    sprite.center_x = 190
    assert arcade.has_collision_with_list(sprite, sprite_list, method=method) is False

    assert arcade.has_collision_with_list(sprite, arcade.SpriteList(), method=method) is False


def test_has_collision_with_list_stops_at_first_hit(window, monkeypatch):
    """has_collision_with_list checks no more sprites than it needs to"""
    from arcade.sprite_list import collision

    sprite = arcade.SpriteSolidColor(10, 10)
    sprite_list = arcade.SpriteList()
    for _ in range(10):
        sprite_list.append(arcade.SpriteSolidColor(10, 10))

    checked = []
    original = collision._check_for_collision

    def counting(sprite1, sprite2):
        checked.append(sprite2)
        return original(sprite1, sprite2)

    monkeypatch.setattr(collision, "_check_for_collision", counting)
    assert arcade.has_collision_with_list(sprite, sprite_list) is True
    assert checked == [sprite_list[0]]

    checked.clear()
    assert arcade.has_collision_with_lists(sprite, [arcade.SpriteList(), sprite_list]) is True
    assert checked == [sprite_list[0]]


def test_has_collision_with_lists(window):
    sprite = arcade.SpriteSolidColor(10, 10)
    near = arcade.SpriteSolidColor(10, 10, center_x=5)
    far = arcade.SpriteList()
    far.append(arcade.SpriteSolidColor(10, 10, center_x=100))
    hit = arcade.SpriteList(use_spatial_hash=True)
    hit.append(near)

    assert arcade.has_collision_with_lists(sprite, []) is False
    assert arcade.has_collision_with_lists(sprite, [far]) is False
    assert arcade.has_collision_with_lists(sprite, [far, hit]) is True
    assert arcade.has_collision_with_lists(sprite, (sl for sl in [far, hit])) is True

    with pytest.raises(TypeError):
        arcade.has_collision_with_lists("moo", [far])


def test_has_collision_with_list_type_errors(window):
    sprite = arcade.SpriteSolidColor(10, 10)
    with pytest.raises(TypeError):
        arcade.has_collision_with_list("moo", arcade.SpriteList())
    with pytest.raises(TypeError):
        arcade.has_collision_with_list(sprite, "moo")


@pytest.mark.parametrize("spatial", [False, True])
def test_check_for_collision_between_lists(window, spatial):
    bullets = arcade.SpriteList()
    for x in (0, 100, 300):
        bullets.append(arcade.SpriteSolidColor(4, 4, center_x=x))
    enemies = arcade.SpriteList(use_spatial_hash=spatial)
    for x in (2, 98, 104, 500):
        enemies.append(arcade.SpriteSolidColor(10, 10, center_x=x))

    pairs = arcade.check_for_collision_between_lists(bullets, enemies)
    expected = [
        (bullets[0], enemies[0]),
        (bullets[1], enemies[1]),
        (bullets[1], enemies[2]),  # One bullet can hit two enemies
    ]
    # A spatial hash returns sprites in no particular order
    assert len(pairs) == len(expected)
    assert set(pairs) == set(expected)

    # Each pair matches check_for_collision
    for a, b in pairs:
        assert arcade.check_for_collision(a, b)

    # Swapping the lists swaps the pairs
    swapped = arcade.check_for_collision_between_lists(enemies, bullets)
    assert len(swapped) == len(expected)
    assert set(swapped) == {(b, a) for a, b in expected}

    # Empty lists
    assert arcade.check_for_collision_between_lists(bullets, arcade.SpriteList()) == []
    assert arcade.check_for_collision_between_lists(arcade.SpriteList(), enemies) == []


@pytest.mark.parametrize("spatial", [False, True])
def test_check_for_collision_between_lists_same_list(window, spatial):
    """With the same list twice, each pair is returned once and never a sprite with itself"""
    sprites = arcade.SpriteList(use_spatial_hash=spatial)
    for x in (0, 5, 8, 100):
        sprites.append(arcade.SpriteSolidColor(10, 10, center_x=x))
    a, b, c, far = sprites

    pairs = arcade.check_for_collision_between_lists(sprites, sprites)
    assert len(pairs) == 3
    assert {frozenset(pair) for pair in pairs} == {
        frozenset((a, b)),
        frozenset((a, c)),
        frozenset((b, c)),
    }


def test_check_for_collision_between_lists_shared_sprite(window):
    """A sprite in both lists isn't paired with itself"""
    shared = arcade.SpriteSolidColor(10, 10)
    other = arcade.SpriteSolidColor(10, 10, center_x=5)
    list_a = arcade.SpriteList()
    list_a.append(shared)
    list_b = arcade.SpriteList()
    list_b.extend([shared, other])
    assert arcade.check_for_collision_between_lists(list_a, list_b) == [(shared, other)]


def test_check_for_collision_between_lists_type_errors(window):
    with pytest.raises(TypeError):
        arcade.check_for_collision_between_lists("moo", arcade.SpriteList())
    with pytest.raises(TypeError):
        arcade.check_for_collision_between_lists(arcade.SpriteList(), "moo")


@pytest.mark.parametrize(
    "wall_scale, bullet_scale",
    [
        ((1, 1), (1, 1)),
        ((-1, 1), (1, 1)),
        ((1, -1), (1, 1)),
        ((-1, -1), (1, 1)),
        ((1, 1), (-1, -1)),
        ((-1, -1), (-1, -1)),
    ],
)
def test_gpu_collision_flipped_sprites(window, wall_scale, bullet_scale):
    """The GPU path finds sprites flipped with a negative scale"""
    if window.ctx._gl_api == "webgl":
        pytest.skip("GPU collision isn't supported on WebGL")

    # A long wall and a small bullet near its end, so only the wall's own
    # size can bring them close enough
    wall = arcade.SpriteSolidColor(200, 20)
    wall.scale = wall_scale
    walls = arcade.SpriteList()
    walls.append(wall)
    bullet = arcade.SpriteSolidColor(4, 4, center_x=80)
    bullet.scale = bullet_scale

    assert walls.get_nearby_sprites_gpu(bullet.position, bullet.size) == [wall]
    gpu = arcade.CollisionMethod.GPU
    assert arcade.check_for_collision_with_list(bullet, walls, method=gpu) == [wall]

    # And still not when it's far away
    bullet.position = 400, 0
    assert walls.get_nearby_sprites_gpu(bullet.position, bullet.size) == []
    assert arcade.check_for_collision_with_list(bullet, walls, method=gpu) == []


def test_check_for_collision_with_list(window):
    # TODO: Check that the right collision function is called internally
    a = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    sl = arcade.SpriteList()
    for y in range(40):
        for x in range(40):
            sprite = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
            sprite.position = x * 50, y * 50
            sl.append(sprite)

    # There's no good way to perform this test with arcade-accelerate enabled.
    # It causes a very different exception that without the inclusion of pyo3
    # into Arcade would be next to impossible to test for in a sane way.
    if not window.using_accelerate:
        with pytest.raises(TypeError):
            arcade.check_for_collision_with_list("moo", sl)
        with pytest.raises(TypeError):
            arcade.check_for_collision_with_list(a, "moo")

    a.position = 100, 100
    assert len(arcade.check_for_collision_with_list(a, sl)) == 1
    a.position = 75, 75
    assert len(arcade.check_for_collision_with_list(a, sl)) == 4

    # With spatial hash
    sl.enable_spatial_hashing()
    a.position = 100, 100
    assert len(arcade.check_for_collision_with_list(a, sl)) == 1
    a.position = 75, 75
    assert len(arcade.check_for_collision_with_list(a, sl)) == 4


def test_check_for_collision_with_lists(window):
    # TODO: Check that the right collision function is called internally
    a = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    sls = []
    for y in range(10):
        for x in range(10):
            sprite = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
            sprite.position = x * 50, y * 50
            sl = arcade.SpriteList()
            sl.append(sprite)
            sls.append(sl)

    # There's no good way to perform this test with arcade-accelerate enabled.
    # It causes a very different exception that without the inclusion of pyo3
    # into Arcade would be next to impossible to test for in a sane way.
    if not window.using_accelerate:
        with pytest.raises(TypeError):
            arcade.check_for_collision_with_lists("moo", sl)

    a.position = 100, 100
    assert len(arcade.check_for_collision_with_lists(a, sls)) == 1
    a.position = 75, 75
    assert len(arcade.check_for_collision_with_lists(a, sls)) == 4

    # With spatial hash
    for sl in sls:
        sl.enable_spatial_hashing()
    a.position = 100, 100
    assert len(arcade.check_for_collision_with_lists(a, sls)) == 1
    a.position = 75, 75
    assert len(arcade.check_for_collision_with_lists(a, sls)) == 4


def test_get_sprites_at_point(window):
    a = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    b = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    sp = arcade.SpriteList()
    sp.extend((a, b))

    with pytest.raises(TypeError):
        arcade.get_sprites_at_point((0, 0), "moo")

    assert set(arcade.get_sprites_at_point((0, 0), sp)) == set([a, b])
    b.position = 100, 0
    assert set(arcade.get_sprites_at_point((0, 0), sp)) == set([a])
    a.position = -100, 0
    assert set(arcade.get_sprites_at_point((0, 0), sp)) == set()

    # With spatial hash
    sp = arcade.SpriteList(use_spatial_hash=True)
    a.position = 0, 0
    b.position = 0, 0
    sp.extend((a, b))
    assert set(arcade.get_sprites_at_point((0, 0), sp)) == set([a, b])
    b.position = 1000, 0
    assert set(arcade.get_sprites_at_point((0, 0), sp)) == set([a])
    a.position = -1000, 0
    assert set(arcade.get_sprites_at_point((0, 0), sp)) == set()


def test_get_sprites_at_exact_point(window):
    a = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    b = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    sp = arcade.SpriteList()
    sp.extend((a, b))

    with pytest.raises(TypeError):
        arcade.get_sprites_at_exact_point((0, 0), "moo")

    assert set(arcade.get_sprites_at_exact_point((0, 0), sp)) == set([a, b])
    b.position = 1, 0
    assert set(arcade.get_sprites_at_exact_point((0, 0), sp)) == set([a])
    a.position = -1, 0
    assert set(arcade.get_sprites_at_exact_point((0, 0), sp)) == set()

    # With spatial hash
    sp = arcade.SpriteList(use_spatial_hash=True)
    sp.extend((a, b))
    a.position = 0, 0
    b.position = 0, 0
    assert set(arcade.get_sprites_at_exact_point((0, 0), sp)) == set([a, b])
    b.position = 1, 0
    assert set(arcade.get_sprites_at_exact_point((0, 0), sp)) == set([a])
    a.position = -1, 0
    assert set(arcade.get_sprites_at_exact_point((0, 0), sp)) == set()


@pytest.mark.parametrize("use_spatial_hash", [True, False])
def test_get_sprites_in_rect(use_spatial_hash):
    a = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED, center_x=50)
    b = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED, center_x=-50)
    c = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED, center_y=50)
    d = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED, center_y=-50)
    sp = arcade.SpriteList(use_spatial_hash=use_spatial_hash)
    sp.extend((a, b, c, d))

    with pytest.raises(TypeError):
        arcade.get_sprites_in_rect(arcade.LRBT(0, 0, 10, 10), "moo")

    assert set(arcade.get_sprites_in_rect(arcade.LRBT(-50, 50, -50, 50), sp)) == {a, b, c, d}
    assert set(arcade.get_sprites_in_rect(arcade.LRBT(100, 200, 100, 200), sp)) == set()
    assert set(arcade.get_sprites_in_rect(arcade.LRBT(-100, 0, -100, 0), sp)) == {b, d}
    assert set(arcade.get_sprites_in_rect(arcade.LRBT(100, 0, 100, 0), sp)) == {a, c}


def test_cpu_collision_with_lazy_list(window):
    """
    Do GPU collision check with lazy list.
    This ensures that check_for_collision_with_list() will trigger
    a spritelist initialization if his is not done yet.
    """
    sprite = arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED)
    spritelist = arcade.SpriteList(lazy=True)
    spritelist.append(arcade.SpriteSolidColor(50, 50, color=arcade.csscolor.RED))
    arcade.check_for_collision_with_list(sprite, spritelist, method=2)


def _reference_check_for_collision(sprite1, sprite2):
    """Collision check using a separating axis test on every edge."""
    poly_a = sprite1.hit_box.get_adjusted_points()
    poly_b = sprite2.hit_box.get_adjusted_points()
    # Also test the x and y axes. Testing only edge normals can miss a
    # separation when a hit box is concave, which detailed ones can be.
    x_a, y_a = zip(*poly_a)
    x_b, y_b = zip(*poly_b)
    if max(x_a) <= min(x_b) or max(x_b) <= min(x_a) or max(y_a) <= min(y_b) or max(y_b) <= min(y_a):
        return False
    for polygon in (poly_a, poly_b):
        for i in range(len(polygon)):
            p1, p2 = polygon[i], polygon[(i + 1) % len(polygon)]
            normal = (p2[1] - p1[1], p1[0] - p2[0])
            projected_a = [normal[0] * p[0] + normal[1] * p[1] for p in poly_a]
            projected_b = [normal[0] * p[0] + normal[1] * p[1] for p in poly_b]
            if max(projected_a) <= min(projected_b) or max(projected_b) <= min(projected_a):
                return False
    return True


def test_check_for_collision_matches_reference():
    """Compare against a full polygon test for many random sprite pairs."""
    rng = random.Random(4321)
    textures = [
        arcade.load_texture(":resources:images/tiles/grassMid.png"),  # 4 point box
        arcade.load_texture(":resources:images/items/coinGold.png"),  # 8 point octagon
        arcade.load_texture(":resources:images/space_shooter/laserBlue01.png"),  # long & thin
        # Detailed hit box, with more points and possibly concave
        arcade.load_texture(
            ":resources:images/space_shooter/meteorGrey_big1.png",
            hit_box_algorithm=arcade.hitbox.algo_detailed,
        ),
    ]

    def random_sprite(shared_angle):
        sprite = arcade.Sprite(rng.choice(textures))
        # Sometimes use a custom hit box bigger than the texture
        if rng.random() < 0.2:
            points = [(x * 2.5, y * 2.5) for x, y in sprite.texture.hit_box_points]
            sprite.hit_box = arcade.hitbox.HitBox(points)
        sprite.scale =(rng.choice([-1, 1]) * rng.choice([0.25, 0.5, 1, 1.5]),
                        rng.choice([-1, 1]) * rng.choice([0.25, 0.5, 1, 1.5]))  # fmt: skip
        # Often share an angle, so both hit boxes have parallel edges
        if rng.random() < 0.5:
            sprite.angle = shared_angle
        else:
            sprite.angle = rng.choice([0, 0, 90, 180, 30, rng.uniform(0, 360)])
        # Positions on a grid so exact touches happen
        sprite.position = rng.randint(-160, 160) / 2, rng.randint(-160, 160) / 2
        return sprite

    results = {True: 0, False: 0}
    for _ in range(5000):
        shared_angle = rng.choice([0, 90, 180, 270, -90, 45, 30, rng.uniform(-720, 720)])
        a, b = random_sprite(shared_angle), random_sprite(shared_angle)
        expected = _reference_check_for_collision(a, b)
        assert arcade.check_for_collision(a, b) is expected
        assert arcade.check_for_collision(b, a) is expected
        results[expected] += 1
    assert min(results.values()) > 500
