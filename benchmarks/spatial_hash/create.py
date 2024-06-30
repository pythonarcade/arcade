import timeit
import arcade
from arcade import SpatialHash

SPACING = 10
CELL_SIZE = 10

sprites = []
for y in range(100):
    for x in range(100):
        sprite = arcade.SpriteSolidColor(10, 10, center_x=x * 10, center_y=y * 10)
        sprites.append(sprite)


def create(cell_size=CELL_SIZE):
    sh = SpatialHash(cell_size)
    for sprite in sprites:
        sh.insert_object_for_box(sprite)


def create_destroy(cell_size=CELL_SIZE):
    sh = SpatialHash(cell_size)
    for sprite in sprites:
        sh.insert_object_for_box(sprite)
    for sprite in sprites:
        sh.remove_object(sprite)


res = timeit.timeit(create, number=100, globals=globals())
print(res)
res = timeit.timeit(create_destroy, number=100, globals=globals())
print(res)
