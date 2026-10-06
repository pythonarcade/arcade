"""
Pixel Demolition

Every pixel of the Arcade logo is a sprite: about 28,000 of them, or 71,000
with smaller pixels. A turret fires a stream of bullets that knock pixels
loose: each bullet explodes when it hits, and every pixel in the blast flies
off as a piece of debris.

This shows off how many sprites Arcade can draw and check for collisions:

* All the pixels are in one SpriteList, drawn with a single draw() call.
* The pixels are in a spatial hash, so each bullet, and each blast, only
  checks the pixels near it. The cell size is set to 16 pixels, close to the
  sprites' size; the default of 128 would make every check look at hundreds
  of pixels.
* Hit pixels are removed from the list. Many removals in one frame are
  applied together in one pass.

Debris can be moved two ways. Press G to switch:

* As sprites, moved in Python every frame. This is simple, but each piece
  costs a little time every frame.
* On the GPU. Each piece is written to a buffer once, when it's launched,
  and a shader works out where it is from how long ago that was. Moving
  any number of pieces costs almost nothing in Python.

Controls:
    Mouse: aim, hold the button to fire (stops auto fire)
    A: auto fire on/off (rebuilds the logo when it's gone)
    G: debris on the GPU / as Python sprites
    1, 2, 3: pixel size 4, 3, or 2
    + / -: fire rate
    R: rebuild the logo

Artwork: the Arcade logo.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_pixel_demolition
"""

import heapq
import math
import random
import struct
import time
from array import array

import PIL.Image

import arcade
from arcade.gl import BufferDescription

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Pixel Demolition"

LOGO_TOP = WINDOW_HEIGHT - 20
LOGO_HEIGHT = 600
TURRET_POSITION = (WINDOW_WIDTH / 2, 30)

BULLET_SPEED = 1500  # Pixels per second
BLAST_RADIUS = 16  # Pixels within this distance of a hit are knocked loose
BULLET_SPREAD = 2.0  # Degrees
GRAVITY = 900  # Pixels per second squared, for the debris
FIRE_RATES = [15, 30, 60, 120, 240]  # Bullets per second

# The GPU debris buffer holds this many pieces, reusing the oldest
GPU_DEBRIS_CAPACITY = 200_000
# Launch x, y, velocity x, y, color (4 bytes), launch time, spin
DEBRIS_RECORD = struct.Struct("<4f4B2f")

DEBRIS_VERTEX_SHADER = """
#version 330

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

uniform float time;
uniform float gravity;
uniform float size;

// The corners of a square, from -0.5 to 0.5
in vec2 in_vert;
// Per piece of debris, written once when it's launched
in vec2 in_start;
in vec2 in_velocity;
in vec4 in_color;
in float in_launch_time;
in float in_spin;

out vec4 v_color;

void main() {
    float t = time - in_launch_time;
    // Where a thrown object is after t seconds
    vec2 center = in_start + in_velocity * t + vec2(0.0, -0.5 * gravity * t * t);
    float angle = radians(in_spin * t);
    mat2 rotate = mat2(cos(angle), -sin(angle), sin(angle), cos(angle));
    vec2 position = center + rotate * (in_vert * size);
    gl_Position = window.projection * window.view * vec4(position, 0.0, 1.0);
    v_color = in_color;
}
"""

DEBRIS_FRAGMENT_SHADER = """
#version 330

in vec4 v_color;
out vec4 out_color;

void main() {
    out_color = v_color;
}
"""


class GpuDebris:
    """
    Debris moved by a shader. Each piece is written to a buffer once, when
    it's launched, and its position is worked out from the time since then.
    """

    def __init__(self, ctx: arcade.ArcadeContext):
        self.ctx = ctx
        self.program = ctx.program(
            vertex_shader=DEBRIS_VERTEX_SHADER, fragment_shader=DEBRIS_FRAGMENT_SHADER
        )
        self.buffer = ctx.buffer(reserve=GPU_DEBRIS_CAPACITY * DEBRIS_RECORD.size)
        corners = array("f", [-0.5, -0.5, 0.5, -0.5, -0.5, 0.5, 0.5, 0.5])
        self.geometry = ctx.geometry(
            [
                BufferDescription(ctx.buffer(data=corners), "2f", ["in_vert"]),
                BufferDescription(
                    self.buffer,
                    "2f 2f 4f1 1f 1f",
                    ["in_start", "in_velocity", "in_color", "in_launch_time", "in_spin"],
                    instanced=True,
                ),
            ],
            mode=ctx.TRIANGLE_STRIP,
        )
        # Where the next piece goes in the buffer, and how many are in it
        self.next = 0
        self.count = 0
        # When each piece falls off the screen, to count the ones in flight
        self.landing_times: list[float] = []
        self.pending = bytearray()
        self.pending_count = 0

    def launch(self, x, y, velocity_x, velocity_y, color, spin, now):
        self.pending += DEBRIS_RECORD.pack(x, y, velocity_x, velocity_y, *color, now, spin)
        self.pending_count += 1
        # Solve y + vy * t - gravity * t² / 2 = -10 for when it's gone
        a, b, c = -0.5 * GRAVITY, velocity_y, y + 10
        landing = (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)
        heapq.heappush(self.landing_times, now + landing)

    def update(self, now):
        """Write the pieces launched this frame to the buffer"""
        if self.pending_count:
            data = memoryview(self.pending)
            first = min(self.pending_count, GPU_DEBRIS_CAPACITY - self.next)
            size = DEBRIS_RECORD.size
            self.buffer.write(data[: first * size], offset=self.next * size)
            if first < self.pending_count:  # Wrap around to the start
                self.buffer.write(data[first * size :], offset=0)
            self.next = (self.next + self.pending_count) % GPU_DEBRIS_CAPACITY
            self.count = min(self.count + self.pending_count, GPU_DEBRIS_CAPACITY)
            self.pending = bytearray()
            self.pending_count = 0
        while self.landing_times and self.landing_times[0] < now:
            heapq.heappop(self.landing_times)

    def draw(self, now, size):
        if self.count:
            self.program["time"] = now
            self.program["gravity"] = GRAVITY
            self.program["size"] = size
            self.geometry.render(self.program, instances=self.count)

    @property
    def in_flight(self):
        return len(self.landing_times)

    def clear(self):
        self.next = self.count = 0
        self.landing_times.clear()


class SpriteDebris:
    """Debris as sprites, moved in Python every frame"""

    def __init__(self):
        self.sprites = arcade.SpriteList()

    def launch(self, x, y, velocity_x, velocity_y, color, spin, size):
        piece = arcade.SpriteSolidColor(size, size, x, y, color)
        piece.change_x = velocity_x
        piece.change_y = velocity_y
        piece.change_angle = spin
        self.sprites.append(piece)

    def update(self, delta_time):
        fallen = []
        for piece in self.sprites:
            piece.change_y -= GRAVITY * delta_time
            piece.center_x += piece.change_x * delta_time
            piece.center_y += piece.change_y * delta_time
            piece.angle += piece.change_angle * delta_time
            if piece.center_y < -10:
                fallen.append(piece)
        for piece in fallen:
            piece.remove_from_sprite_lists()

    def draw(self):
        self.sprites.draw()

    @property
    def in_flight(self):
        return len(self.sprites)

    def clear(self):
        self.sprites.clear()


class Bullet(arcade.SpriteSolidColor):
    """A bullet flying in a straight line"""

    def __init__(self, x, y, angle):
        super().__init__(3, 20, x, y, arcade.color.YELLOW)
        self.angle = math.degrees(angle)
        self.change_x = math.sin(angle) * BULLET_SPEED
        self.change_y = math.cos(angle) * BULLET_SPEED


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK
        self.pixel_size = 3
        self.pixels = arcade.SpriteList()
        self.bullets: arcade.SpriteList[Bullet] = arcade.SpriteList()
        self.gpu_debris = GpuDebris(self.window.ctx)
        self.sprite_debris = SpriteDebris()
        self.debris_on_gpu = True
        self.fire_rate_index = 3
        self.auto_fire = True
        self.firing = False
        self.aim = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.time = 0.0
        self.fire_timer = 0.0

        self.turret = arcade.SpriteSolidColor(12, 50, *TURRET_POSITION, arcade.color.GRAY)
        self.turret_list = arcade.SpriteList()
        # Not drawn, only used to find the pixels in a blast
        self.blast = arcade.SpriteSolidColor(BLAST_RADIUS * 2, BLAST_RADIUS * 2)
        self.turret_list.append(self.turret)

        # Frame timing for the display, updated a few times a second
        self.frame_times: list[float] = []
        self.update_times: list[float] = []
        self.draw_times: list[float] = []
        self.status_timer = 0.0
        self.status = [
            arcade.Text("", 10, WINDOW_HEIGHT - 24 - i * 22, font_size=13) for i in range(5)
        ]
        self.build_logo()

    def build_logo(self):
        """Make a sprite for every pixel of the logo that isn't transparent"""
        self.bullets.clear()
        self.gpu_debris.clear()
        self.sprite_debris.clear()

        rows = LOGO_HEIGHT // self.pixel_size
        image = PIL.Image.open(arcade.resources.resolve(":resources:/logo.png")).convert("RGBA")
        columns = round(rows * image.width / image.height)
        image = image.resize((columns, rows), PIL.Image.Resampling.LANCZOS)
        data = image.tobytes()

        left = (WINDOW_WIDTH - columns * self.pixel_size) / 2
        size = self.pixel_size
        # A spatial hash cell about the size of the sprites keeps each
        # collision check to the few pixels near a bullet
        self.pixels = arcade.SpriteList(
            use_spatial_hash=True, spatial_hash_cell_size=16, capacity=rows * columns
        )
        sprites = []
        for row in range(rows):
            y = LOGO_TOP - row * size
            for column in range(columns):
                i = (row * columns + column) * 4
                if data[i + 3] > 128:
                    color = (data[i], data[i + 1], data[i + 2], 255)
                    sprites.append(
                        arcade.SpriteSolidColor(size, size, left + column * size, y, color)
                    )
        self.pixels.extend(sprites)
        self.logo_pixel_count = len(sprites)

    def fire(self):
        """Fire one bullet from the turret toward the aim point"""
        x, y = TURRET_POSITION
        angle = math.atan2(self.aim[0] - x, self.aim[1] - y)
        angle += math.radians(random.uniform(-BULLET_SPREAD, BULLET_SPREAD))
        self.bullets.append(Bullet(x, y, angle))

    def on_update(self, delta_time):
        start = time.perf_counter()
        self.time += delta_time

        if self.auto_fire:
            # Sweep back and forth across the logo
            sweep = math.sin(self.time * 0.8)
            self.aim = (WINDOW_WIDTH / 2 + sweep * 330, LOGO_TOP - LOGO_HEIGHT / 2)
        x, y = TURRET_POSITION
        self.turret.angle = math.degrees(math.atan2(self.aim[0] - x, self.aim[1] - y))

        if self.auto_fire or self.firing:
            self.fire_timer += delta_time
            interval = 1 / FIRE_RATES[self.fire_rate_index]
            while self.fire_timer >= interval:
                self.fire_timer -= interval
                self.fire()

        for bullet in self.bullets:
            bullet.center_x += bullet.change_x * delta_time
            bullet.center_y += bullet.change_y * delta_time
            if bullet.center_y > WINDOW_HEIGHT or not 0 < bullet.center_x < WINDOW_WIDTH:
                bullet.remove_from_sprite_lists()
                continue
            if arcade.check_for_collision_with_list(bullet, self.pixels):
                self.explode(bullet)
                bullet.remove_from_sprite_lists()

        self.gpu_debris.update(self.time)
        self.sprite_debris.update(delta_time)

        # With auto fire, start over once the logo is gone and the debris has landed
        debris = self.gpu_debris.in_flight + self.sprite_debris.in_flight
        if self.auto_fire and len(self.pixels) < self.logo_pixel_count * 0.02 and not debris:
            self.build_logo()
        self.update_times.append(time.perf_counter() - start)
        self.frame_times.append(delta_time)
        self.update_status(delta_time)

    def explode(self, bullet):
        """Knock loose every pixel within the blast radius of a bullet"""
        # The spatial hash finds the pixels near a square the size of the
        # blast, and a distance check makes the blast round
        self.blast.position = bullet.position
        x, y = bullet.position
        for pixel in arcade.check_for_collision_with_list(self.blast, self.pixels):
            if math.dist((x, y), pixel.position) <= BLAST_RADIUS:
                self.knock_loose(pixel, bullet)

    def knock_loose(self, pixel, bullet):
        """Remove a pixel and launch it as debris, pushed along by the bullet"""
        pixel.remove_from_sprite_lists()
        velocity_x = bullet.change_x * 0.2 + random.uniform(-150, 150)
        velocity_y = bullet.change_y * 0.2 + random.uniform(-100, 200)
        spin = random.uniform(-720, 720)
        if self.debris_on_gpu:
            self.gpu_debris.launch(
                pixel.center_x, pixel.center_y, velocity_x, velocity_y, pixel.color, spin, self.time
            )
        else:
            self.sprite_debris.launch(
                pixel.center_x, pixel.center_y, velocity_x, velocity_y, pixel.color, spin,
                self.pixel_size,
            )  # fmt: skip

    def update_status(self, delta_time):
        self.status_timer += delta_time
        if self.status_timer < 0.25:
            return
        self.status_timer = 0
        fps = len(self.frame_times) / sum(self.frame_times)
        update_ms = 1000 * sum(self.update_times) / len(self.update_times)
        draw_ms = 1000 * sum(self.draw_times) / max(1, len(self.draw_times))
        self.frame_times.clear()
        self.update_times.clear()
        self.draw_times.clear()
        debris = self.gpu_debris.in_flight + self.sprite_debris.in_flight
        mode = "GPU" if self.debris_on_gpu else "Python sprites"
        auto = "on" if self.auto_fire else "off"
        rate = FIRE_RATES[self.fire_rate_index]
        lines = [
            f"FPS: {fps:.0f}   update: {update_ms:.1f} ms   draw: {draw_ms:.1f} ms",
            f"Pixel sprites: {len(self.pixels):,}   debris: {debris:,}   "
            f"bullets: {len(self.bullets)}",
            f"Debris moved by: {mode} (G)",
            f"Pixel size: {self.pixel_size} (1/2/3)   fire rate: {rate}/s (+/-)   "
            f"auto fire: {auto} (A)",
            "Mouse: aim and fire   R: rebuild the logo",
        ]
        for text, line in zip(self.status, lines):
            text.text = line

    def on_draw(self):
        start = time.perf_counter()
        self.clear()
        self.pixels.draw()
        self.sprite_debris.draw()
        self.gpu_debris.draw(self.time, self.pixel_size)
        self.bullets.draw()
        self.turret_list.draw()
        for line in self.status:
            line.draw()
        self.draw_times.append(time.perf_counter() - start)

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.auto_fire:
            self.aim = (x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        self.auto_fire = False
        self.firing = True
        self.aim = (x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.aim = (x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        self.firing = False

    def on_key_press(self, key, modifiers):
        if key == arcade.key.G:
            self.debris_on_gpu = not self.debris_on_gpu
        elif key == arcade.key.A:
            self.auto_fire = not self.auto_fire
        elif key == arcade.key.R:
            self.build_logo()
        elif key in (arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3):
            self.pixel_size = {arcade.key.KEY_1: 4, arcade.key.KEY_2: 3, arcade.key.KEY_3: 2}[key]
            self.build_logo()
        elif key in (arcade.key.PLUS, arcade.key.EQUAL, arcade.key.NUM_ADD):
            self.fire_rate_index = min(self.fire_rate_index + 1, len(FIRE_RATES) - 1)
        elif key in (arcade.key.MINUS, arcade.key.NUM_SUBTRACT):
            self.fire_rate_index = max(self.fire_rate_index - 1, 0)
        elif key == arcade.key.ESCAPE:
            arcade.exit()


def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.show_view(GameView())
    arcade.run()


if __name__ == "__main__":
    main()
