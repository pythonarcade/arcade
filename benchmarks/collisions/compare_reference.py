"""
Compare check_for_collision with a simple reference on random sprite pairs.

This is a correctness check for changes to the collision code, which can
cover far more cases than the unit tests. The reference tests the x and y
axes and every edge normal of both hit boxes, with no caching or shortcuts.

Run from the repository root:

    python -m benchmarks.collisions.compare_reference [--pairs N] [--seed N]

The sprites use a mix of hit box shapes (including a detailed, possibly
concave one), negative and non-uniform scales, shared and random angles,
and positions on a quarter pixel grid so exact touches are common.
"""

import argparse
import random

import arcade

R = ":resources:images/"


def reference_check_for_collision(sprite1, sprite2) -> bool:
    """Separating axis test on the x and y axes and every edge normal."""
    poly_a = sprite1.hit_box.get_adjusted_points()
    poly_b = sprite2.hit_box.get_adjusted_points()
    if not poly_a or not poly_b:
        return False

    # The x and y axes. Testing only edge normals can miss a separation
    # when a hit box is concave.
    x_a, y_a = zip(*poly_a)
    x_b, y_b = zip(*poly_b)
    if max(x_a) <= min(x_b) or max(x_b) <= min(x_a):
        return False
    if max(y_a) <= min(y_b) or max(y_b) <= min(y_a):
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


def load_textures():
    textures = [
        arcade.load_texture(R + name)
        for name in (
            "tiles/grassMid.png",  # 4 point box
            "items/coinGold.png",  # 8 point octagon
            "space_shooter/laserBlue01.png",  # long and thin
            "animated_characters/female_person/femalePerson_idle.png",
            "space_shooter/meteorGrey_big1.png",
        )
    ]
    textures.append(
        arcade.load_texture(
            R + "space_shooter/meteorGrey_big1.png",
            hit_box_algorithm=arcade.hitbox.algo_detailed,
        )
    )
    return textures


def random_sprite(rng, textures, shared_angle):
    sprite = arcade.Sprite(rng.choice(textures))
    sprite.scale = (
        rng.choice([-1, 1]) * rng.choice([0.25, 0.5, 1, 1.5]),
        rng.choice([-1, 1]) * rng.choice([0.25, 0.5, 1, 1.5]),
    )
    # Often share an angle, so both hit boxes have parallel edges
    if rng.random() < 0.6:
        sprite.angle = shared_angle
    else:
        sprite.angle = rng.choice([0, 90, 180, rng.uniform(0, 360)])
    sprite.position = (
        rng.randint(-100, 100) / rng.choice([1, 2, 4]),
        rng.randint(-100, 100) / rng.choice([1, 2, 4]),
    )
    return sprite


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--pairs", type=int, default=200_000, help="number of pairs to test")
    parser.add_argument("--seed", type=int, default=0, help="random seed")
    args = parser.parse_args()

    print(f"arcade {arcade.version.VERSION} from {arcade.__file__}")
    rng = random.Random(args.seed)
    textures = load_textures()
    colliding = mismatches = 0

    for _ in range(args.pairs):
        shared_angle = rng.choice([0, 90, 180, 270, -90, 45, 30, 450, rng.uniform(-720, 720)])
        a = random_sprite(rng, textures, shared_angle)
        b = random_sprite(rng, textures, shared_angle)

        expected = reference_check_for_collision(a, b)
        colliding += expected
        results = arcade.check_for_collision(a, b), arcade.check_for_collision(b, a)
        if results != (expected, expected):
            mismatches += 1
            if mismatches <= 5:
                print(
                    f"MISMATCH expected {expected}, got {results}: "
                    f"angles {a.angle}, {b.angle} scales {a.scale}, {b.scale} "
                    f"positions {a.position}, {b.position}"
                )

    print(f"pairs {args.pairs}, colliding {colliding}, mismatches {mismatches}")
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
