"""
Particle system stress test

Run a particle system that spawns, updates, draws and reaps many particles every frame for performance testing.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_list_particle_fireworks
"""
import os
import arcade
from arcade.examples.frametime_plotter import FrametimePlotter

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Particle stress test"
TEXTURE = "images/pool_cue_ball.png"


def make_emitter():
    return arcade.Emitter(
        center_xy=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2),
        emit_controller=arcade.EmitterIntervalWithTime(0.0004, 15.0),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), 5.0),
            lifetime=1.0,
            scale=0.5,
            alpha=128
        )
    )

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.emitter = make_emitter()
        arcade.set_background_color(arcade.color.BLACK)
        self.frametime_plotter = FrametimePlotter()

    def update(self, delta_time):
        self.emitter.update()
        if self.emitter.can_reap():
            arcade.close_window()
        self.frametime_plotter.end_frame(delta_time)

    def on_draw(self):
        arcade.start_render()
        self.emitter.draw()

if __name__ == "__main__":
    app = MyGame()
    arcade.run()
    app.frametime_plotter.show()