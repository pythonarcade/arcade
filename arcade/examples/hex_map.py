"""
Hex Map Example

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.hex_map
"""

import math
from operator import add

from pyglet.math import Vec2

import arcade
from arcade import hexagon

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Hex Map"


class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):
        super().__init__()

        # Variable to hold our Tiled Map
        self.tile_map: arcade.TileMap

        # Replacing all of our SpriteLists with a Scene variable
        self.scene: arcade.Scene

        # A variable to store our camera object
        self.camera: arcade.camera.Camera2D

        # A variable to store our gui camera object
        self.gui_camera: arcade.camera.Camera2D

        # Initialize the mouse_pan variable
        self.mouse_pan = False

    def reset(self):
        """Reset the game to the initial state."""
        # Do changes needed to restart the game here

        # Tiled always uses pointy orientations
        orientation = hexagon.pointy_orientation
        #
        hex_size_x = 120 / math.sqrt(3)
        hex_size_y = 140 / 2
        map_origin = Vec2(0, 0)

        hex_layout = hexagon.Layout(
            orientation=orientation,
            size=Vec2(hex_size_x, hex_size_y),
            origin=map_origin,
        )

        # Load our TileMap
        self.tile_map = arcade.load_tilemap(
            ":resources:tiled_maps/hex_map.tmj",
            hex_layout=hex_layout,
            use_spatial_hash=True,
        )

        # Create our Scene Based on the TileMap
        self.scene = arcade.Scene.from_tilemap(self.tile_map)  # type: ignore[arg-type]

        # Initialize our camera, setting a viewport the size of our window.
        self.camera = arcade.camera.Camera2D()
        self.camera.zoom = 0.5

        # Initialize our gui camera, initial settings are the same as our world camera.
        self.gui_camera = arcade.camera.Camera2D()

        # Set the background color to a nice red
        self.background_color = arcade.color.BLACK

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        with self.camera.activate():
            self.scene.draw()

        # Call draw() on all your sprite lists below

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        pass

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        pass

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        pass

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        if self.mouse_pan:
            # If the middle mouse button is pressed, we want to pan the camera
            # by the amount of pixels the mouse moved, divided by the zoom level
            # to keep the panning speed consistent regardless of zoom level.
            # The camera position is updated by adding the delta_x and delta_y
            # values to the current camera position, divided by the zoom level.
            # This is done using the add function from the operator module to
            # add the delta_x and delta_y values to the current camera position.
            self.camera.position = tuple(
                map(
                    add,
                    self.camera.position,
                    (-delta_x * 1 / self.camera.zoom, -delta_y * 1 / self.camera.zoom),
                )
            )
            return

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        if button == arcade.MOUSE_BUTTON_MIDDLE:
            self.mouse_pan = True
            return

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        if button == arcade.MOUSE_BUTTON_MIDDLE:
            self.mouse_pan = False
            return

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        """Called whenever the mouse scrolls."""
        # If the mouse wheel is scrolled, we want to zoom the camera in or out
        # by the amount of scroll_y. The zoom level is adjusted by adding the
        # scroll_y value multiplied by a zoom factor (0.1 in this case) to the
        # current zoom level. This allows for smooth zooming in and out of the
        # camera view.

        self.camera.zoom += scroll_y * 0.1

        # The zoom level is clamped to a minimum of 0.1 to prevent the camera
        # from zooming out too far.
        if self.camera.zoom < 0.1:
            self.camera.zoom = 0.1

        # The zoom level is clamped to a maximum of 10 to prevent the camera
        # from zooming in too far.
        if self.camera.zoom > 2:
            self.camera.zoom = 2


def main():
    """Main function"""
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create and setup the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Reset the game to the initial state
    game.reset()

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
