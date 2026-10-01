"""
Micro-benchmarks for sprite collision checks.

Prints the time per call in microseconds. Run from the repository root:

    python -m benchmarks.collisions.micro

To compare two versions, run it on each and compare the output. Timings
vary a few percent between runs, so only trust larger differences.
"""

import random
import timeit

import arcade
from arcade import check_for_collision, check_for_collision_with_list
from arcade.geometry import are_polygons_intersecting

R = ":resources:images/"
BOX = R + "tiles/grassMid.png"  # 4 point box hit box
COIN = R + "items/coinGold.png"  # 8 point octagon hit box
PLAYER = R + "animated_characters/female_person/femalePerson_idle.png"  # 8 points
LASER = R + "space_shooter/laserBlue01.png"  # long and thin
METEOR = R + "space_shooter/meteorGrey_big1.png"


def bench(label, func, number=100_000, repeat=5):
    """Print the best time per call, in microseconds."""
    seconds = min(timeit.repeat(func, number=number, repeat=repeat)) / number
    print(f"{label:<46}{seconds * 1e6:9.3f} us")


def pair(texture_a, texture_b, x, y, angle=0):
    """Two sprites, the first at the origin and the second at (x, y)."""
    a = arcade.Sprite(texture_a) if isinstance(texture_a, str) else texture_a
    b = arcade.Sprite(texture_b) if isinstance(texture_b, str) else texture_b
    a.position = 0, 0
    b.position = x, y
    a.angle = b.angle = angle
    return a, b


def bench_pairs():
    print("--- check_for_collision, one pair")
    cases = {
        "box/box overlap": pair(BOX, BOX, 100, 50),
        "box/box far apart": pair(
            arcade.SpriteSolidColor(64, 64), arcade.SpriteSolidColor(64, 64), 70, 70
        ),
        "octagon/octagon overlap": pair(COIN, COIN, 40, 20),
        "octagon/octagon near-miss": pair(COIN, COIN, 20, 66),
        "octagon/box overlap": pair(PLAYER, BOX, 60, -100),
        "laser/meteor near-miss": pair(LASER, METEOR, 0, 50),
        "octagon/octagon rotated 30 overlap": pair(COIN, COIN, 40, 20, angle=30),
    }
    for label, (a, b) in cases.items():
        result = check_for_collision(a, b)
        bench(f"{label} [{result}]", lambda a=a, b=b: check_for_collision(a, b))

    square_a = [(0, 0), (10, 0), (10, 10), (0, 10)]
    square_b = [(5, 5), (15, 5), (15, 15), (5, 15)]
    bench(
        "are_polygons_intersecting box/box", lambda: are_polygons_intersecting(square_a, square_b)
    )


def bench_changing_pairs():
    print("--- check_for_collision, sprites changing every call")
    a = arcade.Sprite(COIN, center_x=0, center_y=0)
    b = arcade.Sprite(COIN, center_x=40, center_y=20)
    state = {"angle": 0.0}

    def one_moving():
        a.center_x = (a.center_x + 0.37) % 30
        return check_for_collision(a, b)

    def one_rotating():
        state["angle"] = (state["angle"] + 1.7) % 360
        a.angle = state["angle"]
        return check_for_collision(a, b)

    def both_rotating():
        state["angle"] = (state["angle"] + 1.7) % 360
        a.angle = b.angle = state["angle"]
        return check_for_collision(a, b)

    bench("octagon/octagon, one moving", one_moving, number=30_000)
    bench("octagon/octagon, one rotating", one_rotating, number=30_000)
    bench("octagon/octagon, both rotating", both_rotating, number=30_000)


def bench_lists():
    print("--- check_for_collision_with_list")
    # Platformer: a player walking along a row of 400 ground tiles
    walls = arcade.SpriteList()
    for x in range(400):
        walls.append(arcade.Sprite(BOX, scale=0.5, center_x=x * 64, center_y=0))
    player = arcade.Sprite(PLAYER, scale=0.5, center_y=60)  # overlaps the ground slightly

    def walk(method):
        player.center_x = (player.center_x + 1.3) % 25_000
        return check_for_collision_with_list(player, walls, method=method)

    bench("player vs 400 tiles, brute force", lambda: walk(3), number=2_000)
    walls.enable_spatial_hashing()
    bench("player vs 400 tiles, spatial hash", lambda: walk(1), number=20_000)

    # Many sprites close together, so most reach the polygon test
    coins = arcade.SpriteList()
    for i in range(30):
        for j in range(30):
            coins.append(arcade.Sprite(COIN, scale=0.5, center_x=i * 20, center_y=j * 20))
    probe = arcade.Sprite(COIN, scale=0.5, center_x=300, center_y=300)
    bench(
        "coin vs 900 packed coins, brute force",
        lambda: check_for_collision_with_list(probe, coins, method=3),
        number=500,
    )

    # Randomly rotated sprites
    rng = random.Random(1)
    meteors = arcade.SpriteList()
    for _ in range(200):
        meteors.append(
            arcade.Sprite(
                METEOR,
                scale=0.5,
                angle=rng.uniform(0, 360),
                center_x=rng.uniform(0, 400),
                center_y=rng.uniform(0, 400),
            )
        )
    ship = arcade.Sprite(METEOR, scale=0.5, angle=17, center_x=200, center_y=200)
    bench(
        "meteor vs 200 rotated meteors, brute force",
        lambda: check_for_collision_with_list(ship, meteors, method=3),
        number=2_000,
    )


if __name__ == "__main__":
    print(f"arcade {arcade.version.VERSION} from {arcade.__file__}")
    bench_pairs()
    bench_changing_pairs()
    bench_lists()
