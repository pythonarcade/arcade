"""
Runs many operations on all of the sprite's properties
while tracking how long they each take to test performance.
"""
from timeit import Timer
from time import perf_counter_ns
from itertools import cycle
from random import random
from pyglet.math import Vec2
from arcade.sprite import Sprite
from arcade.application import Window
from arcade.sprite_list.sprite_list import SpriteList

timit_count = 100_000

win = Window()
sprite_list = SpriteList(capacity=2)
sprite = Sprite()

sprite_list.append(sprite)
sprite_list.initialize()

is_vec_sprite = isinstance(sprite._velocity, Vec2)

# pre-generate a tuple of random values to void the call cost of random
value_cycle = cycle(tuple(random() for _ in range(10000)))

# Should we write to the gpu
write=False

def creation():
    test_sprite = Sprite()

append_sprite_list = SpriteList(capacity=timit_count, use_spatial_hash=True)
def appending():
    test_sprite = Sprite()
    append_sprite_list.append(test_sprite)

t = (1, 2)
def index_access_tuple():
    a = t[1]

v = Vec2(1, 2)
def index_access_vec():
    a = v[1]

if is_vec_sprite:
    print('USING VECTOR METHODS')
    def scale():
        sprite.scale = Vec2(next(value_cycle), next(value_cycle))
        if write:
            sprite_list.write_sprite_buffers_to_gpu()

    def size():
        sprite.size = Vec2(next(value_cycle), next(value_cycle))
        if write:
            sprite_list.write_sprite_buffers_to_gpu()

    def position():
        sprite.position = Vec2(next(value_cycle), next(value_cycle))
        if write:
            sprite_list.write_sprite_buffers_to_gpu()

    def velocity():
        sprite.velocity = Vec2(next(value_cycle), next(value_cycle))
        if write:
            sprite_list.write_sprite_buffers_to_gpu()
else:
    print('USING TUPLE METHODS')
    def scale():
        sprite.scale = next(value_cycle), next(value_cycle)
        if write:
            sprite_list.write_sprite_buffers_to_gpu()

    def size():
        sprite.size = next(value_cycle), next(value_cycle)
        if write:
            sprite_list.write_sprite_buffers_to_gpu()

    def position():
        sprite.position = next(value_cycle), next(value_cycle)
        if write:
            sprite_list.write_sprite_buffers_to_gpu()

    def velocity():
        sprite.velocity = next(value_cycle), next(value_cycle)
        if write:
            sprite_list.write_sprite_buffers_to_gpu()

def scale_x():
    sprite.scale_x = next(value_cycle)
    if write:
        sprite_list.write_sprite_buffers_to_gpu()

def scale_y():
    sprite.scale_y = next(value_cycle)
    if write:
        sprite_list.write_sprite_buffers_to_gpu()

def width():
    sprite.width = next(value_cycle)
    if write:
        sprite_list.write_sprite_buffers_to_gpu()

def height():
    sprite.height = next(value_cycle)
    if write:
        sprite_list.write_sprite_buffers_to_gpu()

def center_x():
    sprite.center_x = next(value_cycle)
    if write:
        sprite_list.write_sprite_buffers_to_gpu()

def center_y():
    sprite.center_y = next(value_cycle)
    if write:
        sprite_list.write_sprite_buffers_to_gpu()

def change_x():
    sprite.change_x = next(value_cycle)
    if write:
        sprite_list.write_sprite_buffers_to_gpu()

def change_y():
    sprite.change_y = next(value_cycle)
    if write:
        sprite_list.write_sprite_buffers_to_gpu()

# -- Time paired properties --
scale_time = Timer(scale, timer=perf_counter_ns).timeit(timit_count)
size_time = Timer(size, timer=perf_counter_ns).timeit(timit_count)
position_time = Timer(position, timer=perf_counter_ns).timeit(timit_count)
velocity_time = Timer(velocity, timer=perf_counter_ns).timeit(timit_count)

# -- TIme individual properties --
scale_x_time = Timer(scale_x, timer=perf_counter_ns).timeit(timit_count)
scale_y_time = Timer(scale_y, timer=perf_counter_ns).timeit(timit_count)
width_time = Timer(width, timer=perf_counter_ns).timeit(timit_count)
height_time = Timer(height, timer=perf_counter_ns).timeit(timit_count)
center_x_time = Timer(center_x, timer=perf_counter_ns).timeit(timit_count)
center_y_time = Timer(center_y, timer=perf_counter_ns).timeit(timit_count)
change_x_time = Timer(change_x, timer=perf_counter_ns).timeit(timit_count)
change_y_time = Timer(change_y, timer=perf_counter_ns).timeit(timit_count)

# -- Time misc tests --
vec_idx_time = Timer(index_access_vec, timer=perf_counter_ns).timeit(timit_count)
tpl_idx_time = Timer(index_access_tuple, timer=perf_counter_ns).timeit(timit_count)
creation_time = Timer(creation, timer=perf_counter_ns).timeit(timit_count)
append_time = Timer(creation, timer=perf_counter_ns).timeit(timit_count)

times = (scale_time, size_time, position_time, velocity_time, scale_x_time, scale_y_time, width_time, height_time ,center_x_time, center_y_time, change_x_time, change_y_time, vec_idx_time, tpl_idx_time, creation_time, append_time)
time_sum = sum((scale_time, size_time, position_time, velocity_time, scale_x_time, scale_y_time, width_time, height_time ,center_x_time, center_y_time, change_x_time, change_y_time, vec_idx_time, tpl_idx_time, creation_time, append_time)) * 1e-6


print('WITHOUT GPU WRITE')

print(f'call count: {timit_count}, total calls: {timit_count * len(times)}, total_elaped: {time_sum:.3g} ms')
print('scale')
print(f'| - pair   - elapsed: {scale_time * 1e-6:#.3g} ms, avg: {scale_time / timit_count * 1e-6:#.3g} ms')
print(f'| - x      - elapsed: {scale_x_time * 1e-6:#.3g} ms, avg: {scale_x_time / timit_count * 1e-6:#.3g} ms')
print(f'| - y      - elapsed: {scale_y_time * 1e-6:#.3g} ms, avg: {scale_y_time / timit_count * 1e-6:#.3g} ms')
print('size')
print(f'| - pair   - elapsed: {size_time * 1e-6:#.3g} ms, avg: {size_time / timit_count * 1e-6:#.3g} ms')
print(f'| - x      - elapsed: {width_time * 1e-6:#.3g} ms, avg: {width_time / timit_count * 1e-6:#.3g} ms')
print(f'| - y      - elapsed: {height_time * 1e-6:#.3g} ms, avg: {height_time / timit_count * 1e-6:#.3g} ms')
print('position')
print(f'| - pair   - elapsed: {position_time * 1e-6:#.3g} ms, avg: {position_time / timit_count * 1e-6:#.3g} ms')
print(f'| - x      - elapsed: {center_x_time * 1e-6:#.3g} ms, avg: {center_x_time / timit_count * 1e-6:#.3g} ms')
print(f'| - y      - elapsed: {center_y_time * 1e-6:#.3g} ms, avg: {center_y_time / timit_count * 1e-6:#.3g} ms')
print('velocity')
print(f'| - pair   - elapsed: {velocity_time * 1e-6:#.3g} ms, avg: {velocity_time / timit_count * 1e-6:#.3g} ms')
print(f'| - x      - elapsed: {change_x_time * 1e-6:#.3g} ms, avg: {change_x_time / timit_count * 1e-6:#.3g} ms')
print(f'| - y      - elapsed: {change_y_time * 1e-6:#.3g} ms, avg: {change_y_time / timit_count * 1e-6:#.3g} ms')
print('Index')
print(f'| - tuple  - elapsed: {change_x_time * 1e-6:#.3g} ms, avg: {change_x_time / timit_count * 1e-6:#.3g} ms')
print(f'| - vector - elapsed: {change_y_time * 1e-6:#.3g} ms, avg: {change_y_time / timit_count * 1e-6:#.3g} ms')
print('Misc')
print(f'| - create - elapsed: {change_x_time * 1e-6:#.3g} ms, avg: {change_x_time / timit_count * 1e-6:#.3g} ms')
print(f'| - append - elapsed: {change_y_time * 1e-6:#.3g} ms, avg: {change_y_time / timit_count * 1e-6:#.3g} ms')

