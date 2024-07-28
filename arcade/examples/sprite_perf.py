"""
Runs many operations on all of the sprite's properties
while tracking how long they each take to test performance.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_perf
"""
from timeit import Timer
from time import perf_counter_ns
from itertools import cycle
from random import random
from arcade import Vec2, Sprite, SpriteList, Window

win = Window()
sprite_list = SpriteList(capacity=2)
sprite = Sprite()

sprite_list.append(sprite)
sprite_list.initialize()

is_vec_sprite = isinstance(Sprite.position, Vec2)

# pre-generate a tuple of random values to void the call cost of random
value_cycle = cycle(tuple(random() for _ in range(10000)))


if is_vec_sprite:
    def scale():
        sprite.scale = Vec2(next(value_cycle), next(value_cycle))
        sprite_list.write_sprite_buffers_to_gpu()

    def size():
        sprite.size = Vec2(next(value_cycle), next(value_cycle))
        sprite_list.write_sprite_buffers_to_gpu()

    def position():
        sprite.position = Vec2(next(value_cycle), next(value_cycle))
        sprite_list.write_sprite_buffers_to_gpu()

    def velocity():
        sprite.velocity = Vec2(next(value_cycle), next(value_cycle))
        sprite_list.write_sprite_buffers_to_gpu()
else:
    def scale():
        sprite.scale = next(value_cycle), next(value_cycle)
        sprite_list.write_sprite_buffers_to_gpu()

    def size():
        sprite.size = next(value_cycle), next(value_cycle)
        sprite_list.write_sprite_buffers_to_gpu()

    def position():
        sprite.position = next(value_cycle), next(value_cycle)
        sprite_list.write_sprite_buffers_to_gpu()

    def velocity():
        sprite.velocity = next(value_cycle), next(value_cycle)
        sprite_list.write_sprite_buffers_to_gpu()

def scale_x():
    sprite.scale_x = next(value_cycle)
    sprite_list.write_sprite_buffers_to_gpu()

def scale_y():
    sprite.scale_y = next(value_cycle)
    sprite_list.write_sprite_buffers_to_gpu()

def width():
    sprite.width = next(value_cycle)
    sprite_list.write_sprite_buffers_to_gpu()

def height():
    sprite.height = next(value_cycle)
    sprite_list.write_sprite_buffers_to_gpu()

def center_x():
    sprite.center_x = next(value_cycle)
    sprite_list.write_sprite_buffers_to_gpu()

def center_y():
    sprite.center_y = next(value_cycle)
    sprite_list.write_sprite_buffers_to_gpu()

def change_x():
    sprite.change_x = next(value_cycle)
    sprite_list.write_sprite_buffers_to_gpu()

def change_y():
    sprite.change_y = next(value_cycle)
    sprite_list.write_sprite_buffers_to_gpu()


timit_count = 100_000

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

print(f'call count: {timit_count}, total calls: {timit_count * 12}, total_elaped: {sum((scale_time, size_time, position_time, velocity_time, scale_x_time, scale_y_time, width_time, height_time ,center_x_time, center_y_time, change_x_time, change_y_time)) * 1e-6} ms')

print(f'scale    - elapsed: {scale_time * 1e-6} ms, avg: {scale_time / timit_count * 1e-6} ms')
print(f'| - x    - elapsed: {scale_x_time * 1e-6} ms, avg: {scale_x_time / timit_count * 1e-6} ms')
print(f'| - y    - elapsed: {scale_y_time * 1e-6} ms, avg: {scale_y_time / timit_count * 1e-6} ms')

print(f'size     - elapsed: {size_time * 1e-6} ms, avg: {size_time / timit_count * 1e-6} ms')
print(f'| - x    - elapsed: {width_time * 1e-6} ms, avg: {width_time / timit_count * 1e-6} ms')
print(f'| - y    - elapsed: {height_time * 1e-6} ms, avg: {height_time / timit_count * 1e-6} ms')

print(f'position - elapsed: {position_time * 1e-6} ms, avg: {position_time / timit_count * 1e-6} ms')
print(f'| - x    - elapsed: {center_x_time * 1e-6} ms, avg: {center_x_time / timit_count * 1e-6} ms')
print(f'| - y    - elapsed: {center_y_time * 1e-6} ms, avg: {center_y_time / timit_count * 1e-6} ms')

print(f'velocity - elapsed: {velocity_time * 1e-6} ms, avg: {velocity_time / timit_count * 1e-6} ms')
print(f'| - x    - elapsed: {change_x_time * 1e-6} ms, avg: {change_x_time / timit_count * 1e-6} ms')
print(f'| - y    - elapsed: {change_y_time * 1e-6} ms, avg: {change_y_time / timit_count * 1e-6} ms')
