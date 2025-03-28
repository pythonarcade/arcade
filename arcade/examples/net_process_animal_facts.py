"""
Display random animal facts from
* https://github.com/wh-iterabb-it/meowfacts
* https://kinduff.github.io/dog-api/

and random cat images from
* https://cataas.com
* https://random.dog

More free APIs: https://github.com/public-apis/public-apis

This example shows how to use multiprocessing to run a service in a separate process.
The service will run in the background and return data to the main process when it's ready.
This is a good way to keep your main game loop running smoothly while waiting for data.
This method is acceptable for simpler types of games. Some extra latency may be introduced
when using this method.

The example also shows that we can send textures between processes.

Some of these services may go down or change their API, so this code may not work
as expected. If you find a service that is no longer working, please make a pull request!

Controls:
    SPACE: Request a new fact OR wait for the next fact to be displayed
    F: Toggle fullscreen
    ESC: Close the window

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.net_process_animal_facts
"""
import PIL.Image
import random
import traceback
import time
import json
import urllib.request
import multiprocessing as mp
from queue import Empty
import arcade
from arcade.math import clamp

CHOICES = ["meow", "woof"]  # Which facts to display


class GameView(arcade.View):
    """Display a random cat fact"""
    def __init__(self):
        super().__init__()
        self.loading = False
        self.text_fact = arcade.Text(
            "",
            x=self.window.width / 2, y=self.window.height / 2 + 50,
            width=1100, font_size=36, anchor_x="center", anchor_y="center",
            multiline=True,
        )
        self.text_info = arcade.Text(
            "Press SPACE to request new fact",
            font_size=20,
            x=20, y=40, color=arcade.color.LIGHT_BLUE,
        )
        self.angle = 0  # Rotation for the spinning loading initicator
        # Keep track of time to auto request new facts
        self.update_interval = 30  # seconds
        self.last_updated = 0
        # Background image
        self.bg_texture_1 = None
        self.bg_texture_2 = None
        # Keep track of when we last updated the background image (for fading)
        self.bg_updated_time = 0

    def on_draw(self):
        """Draw the next frame"""
        self.clear()

        # Draw a background image fading between two images if needed
        fade = clamp(time.time() - self.bg_updated_time, 0.0, 1.0)
        self.draw_background(self.bg_texture_1, fade * 0.35)
        if fade < 1.0:
            self.draw_background(self.bg_texture_2,  0.35 * (1.0 - fade))

        # Draw the fact text
        self.text_fact.draw()

        # Draw a spinning circle while we wait for a fact
        if self.loading:
            arcade.draw_rect_filled(
                arcade.XYWH(self.window.width - 50, self.window.height - 50, 50, 50),
                color=arcade.color.ORANGE,
                tilt_angle=self.angle,
            )

        # Draw a progress bar to show how long until we request a new fact
        progress = 1.0 - ((time.time() - self.last_updated) / self.update_interval)
        if progress > 0:
            arcade.draw_lrbt_rectangle_filled(
                left=0, right=self.window.width * progress,
                bottom=0, top=20,
                color=arcade.color.LIGHT_KHAKI
            )

        # Draw info text
        self.text_info.draw()

    def draw_background(self, texture: arcade.Texture, alpha: int) -> None:
        """Draw a background image attempting to fill the entire window"""
        if texture is None:
            return

        # Get the highest ratio of width or height to fill the window
        scale = max(self.window.width / texture.width, self.window.height / texture.height)
        arcade.draw_texture_rect(
            texture,
            arcade.XYWH(
                self.window.width / 2,
                self.window.height / 2,
                texture.width * scale,
                texture.height * scale,
            ),
            blend=True,
            alpha=int(alpha * 255),
        )

    def on_update(self, delta_time: float):
        """Update state for the next frame"""
        # Keep spinning the loading indicator
        self.angle += delta_time * 400

        # Request a new fact if it's time to do so
        if time.time() - self.last_updated > self.update_interval:
            self.request_new_fact()

        # Check if we have some new data from the service
        # This is a non-blocking call, so it will return immediately (fast)
        try:
            # Immediately raises Empty exception if there is no data
            data = animal_service.out_queue.get(block=False)
            # If we got a string, it's new fact text
            if isinstance(data, str):
                self.text_fact.text = data
                self.loading = False
                self.last_updated = time.time()
            # If we got a texture, it's a new background image
            elif isinstance(data, arcade.Texture):
                self.bg_texture_2 = self.bg_texture_1
                self.bg_texture_1 = data
                self.bg_updated_time = time.time()
        except Empty:
            pass

    def on_key_press(self, symbol: int, modifiers: int):
        """Handle key presses"""
        if symbol == arcade.key.SPACE:
            self.request_new_fact()
        elif symbol == arcade.key.F:
            self.window.set_fullscreen(not self.window.fullscreen)
            self.window.set_vsync(True)
        elif symbol == arcade.key.ESCAPE:
            self.window.close()

    def request_new_fact(self):
        """Request a new fact from the service unless we're already waiting for one"""
        if not self.loading:
            self.loading = True
            animal_service.in_queue.put(random.choice(CHOICES))

    def on_resize(self, width: float, height: float):
        """Handle window resize events"""
        # Re-position the text to the center of the window
        # and make sure it fits in the window (width)
        self.text_fact.x = width / 2
        self.text_fact.y = height / 2 + 50
        self.text_fact.width = width - 200


class AnimaFactsService:
    """
    A daemon process that will keep running and return random cat facts.
    The process will die with the main process.
    """
    def __init__(self):
        # Queue for sending commands to the process
        self.in_queue = mp.Queue()
        # Queue for receiving data from the process
        self.out_queue = mp.Queue()
        # The process itself. Daemon=True means it will die with the main process.
        self.process = mp.Process(
            target=self.do_work,
            args=(self.in_queue, self.out_queue),
            daemon=True,
        )

    def do_work(self, in_queue, out_queue):
        """Keep pulling the in queue forever and do work when something arrives"""
        fact_types = {
            "meow": CatFacts(),
            "woof": DogFacts(),
        }
        # Keep looping forever waiting for work
        while True:
            # The supported commands are "ready", "meow", and "woof"
            command = in_queue.get(block=True)
            if command == "ready":
                # Signal that the process is ready to receive commands
                out_queue.put("ready")
            else:
                selected_type = fact_types.get(command)
                try:
                    out_queue.put(selected_type.get_fact())
                    out_queue.put(selected_type.get_image())
                except Exception:
                    traceback.print_exc()

    def start(self) -> int:
        """Start the process and wait for it to be ready"""
        self.process.start()
        # Send a ready request and do a blocking get to wait for the response.
        self.in_queue.put("ready")
        self.out_queue.get(block=True)
        return self.process.pid


class Facts:
    """Base class for fact providers"""

    def get_fact(self) -> str:
        raise NotImplementedError()

    def get_image(self) -> arcade.Texture:
        raise NotImplementedError()


class CatFacts(Facts):
    """Get random cat facts and images"""

    def get_fact(self) -> str:
        with urllib.request.urlopen("https://meowfacts.herokuapp.com") as fd:
            data = json.loads(fd.read().decode("utf-8"))
            print(data)
            return data["data"][0]

    def get_image(self) -> arcade.Texture:
        """Get a random cat image from https://cataas.com/"""
        with urllib.request.urlopen("https://cataas.com/cat") as fd:
            return arcade.Texture(PIL.Image.open(fd).convert("RGBA"))


class DogFacts(Facts):
    """Get random dog facts and images"""

    def __init__(self):
        # Fetch the full image list at creation. This is more practical for this api.
        with urllib.request.urlopen("https://random.dog/doggos") as fd:
            self.images = json.loads(fd.read().decode("utf-8"))

        # Remove videos
        self.images = [i for i in self.images if not i.endswith(".mp4")]

    def get_fact(self) -> str:
        with urllib.request.urlopen("https://dogapi.dog/api/v2/facts") as fd:
            data = json.loads(fd.read().decode("utf-8"))
            print(data)
            return data["data"][0]["attributes"]["body"]

    def get_image(self) -> arcade.Texture:
        """Get a random dog image from https://random.dog"""
        name = random.choice(self.images)
        print("Image:", name)
        with urllib.request.urlopen(f"https://random.dog/{name}") as fd:
            return arcade.Texture(PIL.Image.open(fd).convert("RGBA"))


def main():
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(1280, 720, "Random Animal Facts", resizable=True, vsync=True)

    # Create the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()

if __name__ == "__main__":
    """ Main function """
    animal_service = AnimaFactsService()
    print("Starting animal fact service...")
    pid = animal_service.start()
    print("Service started. pid:", pid)

    main()
