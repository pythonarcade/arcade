"""
Removing and re-adding sprite to spatial hash vs moving it in the spatial hash
"""

import timeit
import arcade

CELL_SIZE = 15

sprites = []
for y in range(100):
    for x in range(100):
        sprite = arcade.SpriteSolidColor(10, 10, center_x=x * 10, center_y=y * 10)
        sprites.append(sprite)


def add_remove():
    sh = arcade.SpatialHash(CELL_SIZE)
    for sprite in sprites:
        sh.add(sprite)
    for sprite in sprites:
        sh.remove(sprite)
        sh.add(sprite)


def move():
    sh = arcade.SpatialHash(CELL_SIZE)
    for sprite in sprites:
        sh.add(sprite)
    for sprite in sprites:
        sh.move(sprite)
    # Moves are applied at the next query
    sh.get_sprites_near_point((0, 0))


res_1 = timeit.timeit(add_remove, number=100, globals=globals())
print("add/remove", res_1)
res_2 = timeit.timeit(move, number=100, globals=globals())
print("move", res_2)
print("ratio", res_1 / res_2 * 100)
