"""
Micro-benchmarks for hit box properties and point recalculation.

Prints the time per call in microseconds. Run from the repository root:

    python -m benchmarks.collisions.hit_box
"""

import timeit

import arcade

PLAYER = ":resources:images/animated_characters/female_person/femalePerson_idle.png"


def bench(label, func, number=200_000, repeat=7):
    """Print the best time per call, in microseconds."""
    seconds = min(timeit.repeat(func, number=number, repeat=repeat)) / number
    print(f"{label:<46}{seconds * 1e6:9.3f} us")


def bench_bounds():
    print("--- left/right/bottom/top")
    sprite = arcade.Sprite(PLAYER)

    def all_four():
        return sprite.left, sprite.right, sprite.bottom, sprite.top

    def all_four_after_move():
        sprite.center_x += 1
        return sprite.left, sprite.right, sprite.bottom, sprite.top

    def one_after_move():
        sprite.center_x += 1
        return sprite.left

    def adjusted_bounds_after_move():
        sprite.center_x += 1
        return sprite.hit_box.get_adjusted_bounds()

    bench("all four, not moving", all_four)
    bench("all four, after a move", all_four_after_move)
    bench("left only, after a move", one_after_move)
    bench("get_adjusted_bounds(), after a move", adjusted_bounds_after_move)


def bench_adjusted_points():
    print("--- get_adjusted_points() recalculation")
    hit_box = arcade.hitbox.RotatableHitBox(arcade.Sprite(PLAYER).hit_box.points)

    for angle in (0, 30, 90):

        def recalculate(angle=angle):
            hit_box.angle = angle  # Marks the points as changed
            return hit_box.get_adjusted_points()

        bench(f"angle {angle}", recalculate)


if __name__ == "__main__":
    print(f"arcade {arcade.version.VERSION} from {arcade.__file__}")
    bench_bounds()
    bench_adjusted_points()
