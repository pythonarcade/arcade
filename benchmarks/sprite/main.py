"""
Quick and dirty system measuring differences between two sprite classes.
"""
import gc
import math
import timeit
import arcade
from itertools import cycle
from random import random

from sprite_alt import BasicSprite as SpriteA
from arcade import BasicSprite as SpriteB

random_numbers = cycle(tuple(random() + 0.1 for _ in range(1009)))

N = 100
MEASUREMENT_CONFIG = [
    {"name": "populate", "number": N, "measure_method": "populate", "post_methods": ["flush"]},
    {"name": "scale_set", "number": N, "measure_method": "scale_set", "post_methods": []},
    {"name": "scale_set_uniform", "number": N, "measure_method": "scale_set_uniform", "post_methods": []},
    {"name": "scale_mult", "number": N, "measure_method": "scale_mult", "post_methods": []},
    {"name": "scale_mult_uniform", "number": N, "measure_method": "scale_mult_uniform", "post_methods": []},
]


class Measurement:
    def __init__(self, avg=0.0, min=0.0, max=0.0):
        self.avg = avg
        self.min = min
        self.max = max

    @classmethod
    def from_values(cls, values: list[float]) -> "Measurement":
        return cls(avg=sum(values) / len(values), min=min(values), max=max(values))

    # TODO: Compare measurements

    def __str__(self):
        return f"avg={self.avg}, min={self.min}, max={self.max}"


class SpriteCollection:
    sprite_type = None
    sprite_count = 100_000

    def __init__(self):
        self.spritelist = arcade.SpriteList(lazy=True, capacity=self.sprite_count)

    def flush(self):
        """Remove all sprites from the spritelist."""
        self.spritelist.clear()

    def populate(self):
        """Populate the spritelist with sprites."""
        texture = arcade.load_texture(":assets:images/items/coinBronze.png")
        N = int(math.sqrt(self.sprite_count))
        for y in range(N):
            for x in range(N):
                self.spritelist.append(
                    self.sprite_type(
                        texture=texture,
                        center_x=x * 64,
                        center_y=y * 64,
                        scale=(1.0, 1.0),
                    )
                )

    # Scale
    def scale_set(self):
        """Set the scale of all sprites."""
        for sprite in self.spritelist:
            sprite.scale = next(random_numbers)

    def scale_set_uniform(self):
        """Set the scale of all sprites."""
        for sprite in self.spritelist:
            sprite.scale_set_uniform(next(random_numbers))

    def scale_mult_uniform(self):
        """Multiply the scale of all sprites."""
        for sprite in self.spritelist:
            sprite.scale_multiply_uniform(next(random_numbers))

    def scale_mult(self):
        """Multiply the scale of all sprites uniformly."""
        for sprite in self.spritelist:
            sprite.multiply_scale(next(random_numbers, 1.0))

    # Rotate
    # Move
    # Collision detection


class SpriteCollectionA(SpriteCollection):
    sprite_type = SpriteA

class SpriteCollectionB(SpriteCollection):
    sprite_type = SpriteB


def measure_sprite_collection(collection: SpriteCollection, number=10) -> dict[str, Measurement]:
    """Perform actions on the sprite collections and measure the time."""
    print(f"Measuring {collection.__class__.__name__}...")
    measurements: dict[str, Measurement] = {}

    for config in MEASUREMENT_CONFIG:
        name = config["name"]
        number = config["number"]
        measure_method = getattr(collection, config["measure_method"])
        post_methods = [getattr(collection, method) for method in config.get("post_methods", [])]

        results = []
        try:
            for _ in range(number):
                results.append(timeit.timeit(measure_method, number=1))
                for method in post_methods:
                    method()
            measurement = Measurement.from_values(results)
            measurements[name] = measurement
            print(f"{name}: {measurement}")
        except Exception as e:
            print(f"Failed to measure {name}: {e}")

        collection.flush()
        collection.populate()
        gc_until_nothing()

    return measurements


def gc_until_nothing():
    """Run the garbage collector until no more objects are found."""
    while gc.collect():
        pass


def main():
    a = SpriteCollectionA()
    b = SpriteCollectionB()

    m1 = measure_sprite_collection(a)
    gc_until_nothing()
    m2 = measure_sprite_collection(b)
    # FIXME: Compare measurements


if __name__ == '__main__':
    main()
