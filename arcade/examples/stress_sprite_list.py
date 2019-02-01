"""
SpriteList Stress Test

Simple program using SpriteList.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.stress_sprite_list
"""

import random
import arcade
import os
import collections
import time

import cProfile, pstats
import pyglet

pr = cProfile.Profile()
pr.enable()

# --- Constants ---
METEOR_COUNT = 500

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "SpriteList Stress Test"


class FPSCounter:
    def __init__(self):
        self.time = time.perf_counter()
        self.frame_times = collections.deque(maxlen=60)

    def tick(self):
        t1 = time.perf_counter()
        dt = t1 - self.time
        self.time = t1
        self.frame_times.append(dt)

    def get_fps(self):
        return len(self.frame_times) / sum(self.frame_times)


class MyGame(arcade.Window):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Variables that will hold sprite lists
        self.meteor_list = None

        arcade.set_background_color(arcade.color.OUTER_SPACE)

        self.fps = FPSCounter()

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.meteor_list = arcade.SpriteList(use_spatial_hash=False)

        # Set up the meteors
        images = [
            "meteorGrey_big1.png",
            "meteorGrey_big2.png",
            "meteorGrey_big3.png",
            "meteorGrey_big4.png",
            "meteorGrey_med1.png",
            "meteorGrey_med2.png",
            "meteorGrey_small1.png",
            "meteorGrey_small2.png",
            "meteorGrey_tiny1.png",
            "meteorGrey_tiny2.png",
        ]

        # Create the meteors
        for i in range(METEOR_COUNT):

            meteor = Meteor(f"images/{random.choice(images)}")

            # Position the meteor
            meteor.center_x = random.randrange(SCREEN_WIDTH)
            meteor.center_y = random.randrange(SCREEN_HEIGHT)
            # Assign random speed
            meteor.change_x = (random.random() - 0.5) * 2
            meteor.change_y = (random.random() - 0.5) * 2

            # Add the meteor to the lists
            self.meteor_list.append(meteor)

        arcade.window_commands.schedule(self.show_fps, 1)

    def on_draw(self):
        """ Draw everything """
        arcade.start_render()
        self.meteor_list.draw()

    def update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.meteor_list.update()
        self.fps.tick()

    def show_fps(self, dt):
        print(self.fps.get_fps())


class Meteor(arcade.Sprite):
    def update(self):
        super().update()
        if self.center_x > SCREEN_WIDTH:
            self.center_x = 0
        elif self.center_x < 0:
            self.center_x = SCREEN_WIDTH
        if self.center_y > SCREEN_HEIGHT:
            self.center_y = 0
        elif self.center_y < 0:
            self.center_y = SCREEN_HEIGHT


def report(dt):
    pr.disable()
    with open("stress_sprite_list_stats.txt", "w") as f:
        sortby = 'tottime'
        ps = pstats.Stats(pr, stream=f).sort_stats(sortby)
        ps.print_stats()
    print("Report written")


pyglet.clock.schedule_once(report, 5)


def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
