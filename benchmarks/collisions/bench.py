import math
import arcade
import pyglet
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WALL_DIM_MIN = 10
WALL_DIM_MAX = 200
WALLS_COUNT = 10

BULLET_VELOCITY_MIN = 1 / 60
BULLET_VELOCITY_MAX = 10 / 60
BULLET_COUNT = 1000

SIMULATE_MINUTES = 1
SIMULATE_FPS = 60

# Predictable randomization so that each benchmark is identical
rng = random.Random(0)

bullets = arcade.SpriteList()
walls = arcade.SpriteList()

window = arcade.Window()

# Seed chosen manually to create a wall distribution that looked good enough,
# like something I might create in a game.
rng.seed(2)
for i in range(0, WALLS_COUNT):
    wall = arcade.SpriteSolidColor(
        rng.randint(WALL_DIM_MIN, WALL_DIM_MAX), rng.randint(WALL_DIM_MIN, WALL_DIM_MAX), arcade.color.BLACK
    )
    wall.position = rng.randint(0, SCREEN_WIDTH), rng.randint(0, SCREEN_HEIGHT)
    walls.append(wall)

for i in range(0, BULLET_COUNT):
    # Create a new bullet
    new_bullet = arcade.SpriteCircle(color=arcade.color.RED, radius=10)
    new_bullet.position = (rng.randint(0, SCREEN_WIDTH), rng.randint(0, SCREEN_HEIGHT))
    speed = rng.random() * (BULLET_VELOCITY_MAX - BULLET_VELOCITY_MIN) + BULLET_VELOCITY_MIN
    angle = rng.random() * math.pi * 2
    new_bullet.velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
    # Half of bullets are rotated, to test those code paths
    if rng.random() > 0.5:
        new_bullet.angle = 45
    bullets.append(new_bullet)

for i in range(0, int(SIMULATE_MINUTES * 60 * SIMULATE_FPS)):
    pyglet.clock.tick()

    window.switch_to()
    window.dispatch_events()

    # Move all bullets
    for bullet in bullets:
        bullet.position = (bullet.position[0] + bullet.velocity[0], bullet.position[1] + bullet.velocity[1])

    # Check for collisions
    bullets_w_collision = []
    for bullet in bullets:
        walls_hit = arcade.check_for_collision_with_list(bullet, walls)
        if walls_hit:
            bullets_w_collision.append(bullet)
    for bullet in bullets_w_collision:
        # bullets.remove(bullet)
        bullet.position = (rng.randint(0, SCREEN_WIDTH), rng.randint(0, SCREEN_HEIGHT))

    window.dispatch_event("on_draw")

    window.clear(color=arcade.color.WHITE)
    walls.draw()
    bullets.draw()
    window.flip()
