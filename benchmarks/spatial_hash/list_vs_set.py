import copy
import arcade
import timeit

sprites = [arcade.SpriteSolidColor(10, 10, center_x=10 * i) for i in range(20)]
sprite_set = set(sprites)


def add_remove_set():
    bucket = set()
    for sprite in sprites:
        bucket.add(sprite)
    for sprite in sprites:
        bucket.remove(sprite)


def add_remove_list():
    bucket = []
    for sprite in sprites:
        bucket.append(sprite)
    for sprite in sprites:
        bucket.remove(sprite)


def copy_set():
    for i in range(100):
        bucket = copy.copy(sprite_set)


def update_set():
    for i in range(100):
        s = set(sprite_set)
        # s.update(sprite_set)


# Set vs list:
# Faster overall with set. Slower to add, much faster to remove.
print("Set vs list")
res = timeit.timeit(add_remove_set, number=10000)
print(res)
res = timeit.timeit(add_remove_list, number=10000)
print(res)

# Copy vs update
print("Copy vs update")
res = timeit.timeit(copy_set, number=10000)
print(res)
res = timeit.timeit(update_set, number=10000)
print(res)
