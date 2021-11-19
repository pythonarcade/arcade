import math
import time
import arcade

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Basic Renderer"


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        # vsync must be off when measuring rendering calls
        self.set_vsync(False)

        start = time.time()
        self.sprites = arcade.SpriteList()
        num_sprites = 100_000
        # sprite_scale = 0.01  # All sprites covering the screen
        sprite_scale = 1.0  # default
        r = int(math.sqrt(num_sprites))
        for y in range(r):
            for x in range(r):
                self.sprites.append(arcade.Sprite(
                    arcade.resources.image_box_crate,
                    scale=sprite_scale,
                    center_x=128 * sprite_scale * x,
                    center_y=128 * sprite_scale * y,
                ))
        self.sprites.draw()  # Force the list to build

        self.sprites.program = self.ctx.sprite_list_program_no_cull
        print(f"Initialization time: {time.time() -start}")

        self.query = self.ctx.query()
        self.frames = 0
        self.frame_step = 600
        self.time_elapsed_total = 0

    def on_draw(self):
        self.clear()

        with self.query:
            self.sprites.draw()

        self.time_elapsed_total += self.query.time_elapsed
        self.frames += 1

        if self.frames % self.frame_step == 0:
            print(f"--- Stats over {self.frame_step} frames")
            print(f"Time elapsed       : {self.time_elapsed_total / 1_000_000_000} seconds")
            print(f"Samples passed     : {self.query.samples_passed}")
            print(f"Primitives created : {self.query.primitives_generated}")
            self.time_elapsed_total = 0


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
