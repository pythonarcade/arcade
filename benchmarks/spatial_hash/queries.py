"""
Benchmark spatial hash queries, and check they don't grow the hash.

Run from the repository root:

    python -m benchmarks.spatial_hash.queries
"""

import timeit

import arcade
from arcade.sprite_list.spatial_hash import SpatialHash
from arcade.types.rect import LRBT


def bench(label, func, number=200_000, repeat=5):
    """Print the best time per call, in microseconds."""
    seconds = min(timeit.repeat(func, number=number, repeat=repeat)) / number
    print(f"{label:<46}{seconds * 1e6:9.3f} us")


def main():
    print(f"arcade {arcade.version.VERSION} from {arcade.__file__}")
    spatial_hash = SpatialHash(cell_size=64)
    for x in range(50):
        spatial_hash.add(arcade.SpriteSolidColor(64, 64, center_x=x * 64, center_y=0))
    print("buckets after adding 50 walls:", len(spatial_hash.contents))

    # Query a large, mostly empty area. This must not add buckets.
    player = arcade.SpriteSolidColor(48, 48)
    for x in range(0, 20_000, 16):
        for y in range(0, 20_000, 400):
            player.position = x, y
            spatial_hash.get_sprites_near_sprite(player)
            spatial_hash.get_sprites_near_point((x, y))
            spatial_hash.get_sprites_near_rect(LRBT(x, x + 10, y, y + 10))
    print("buckets after querying a 20000x20000 area:", len(spatial_hash.contents))

    player.position = 100, 20
    bench("get_sprites_near_sprite", lambda: spatial_hash.get_sprites_near_sprite(player))

    def add_remove():
        spatial_hash.add(player)
        spatial_hash.remove(player)

    bench("add + remove", add_remove)


if __name__ == "__main__":
    main()
