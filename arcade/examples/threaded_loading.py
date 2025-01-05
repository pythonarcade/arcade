"""
Loading large Levels can take a lot of time.
To combat this the process can be offloaded to a separate thread.
Python multi-threading doesn't necessarily speed up your program,
but it can help protect against your game freezing.

This example uses the built-in threading module to load a list of
tiled maps from memory without stopping the rest of the game from
working. This isn't strictly the best way to do such level loading
but it will hopefully explain how it is possible.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.threaded_loading
"""
from __future__ import annotations
import time

# Threading is built into python and provides many tools for
# working with multiple threads
import threading

import arcade
from arcade.color import RED, GREEN, BLUE, WHITE

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = 'Threaded Tilemap Loading'

# Because the tilesets we use aren't all that large this delay helps
# illustrate the utility of threaded loading. You don't need to add this
ARTIFICIAL_DELAY = 1

LEVELS = (
    'test_map_1',
    'test_map_2',
    'test_map_3',
    'test_map_4',  # Intentionally omitted to allow its loading to fail
    'test_map_5',  # Intentionally blank file
    'test_map_6',
    'test_map_7',
)
LEVEL_LOCATION = ':assets:tiled_maps/'
COLUMN_COUNT = 4
LEVEL_RENDERER_SIZE = WINDOW_WIDTH // 5 - 10, WINDOW_HEIGHT // 5 - 10


class LevelLoader:
    """
    While threading Threads run a method its often
    safer to contain the threaded operations inside
    a single object.

    While it is viable to create a thread when it
    is needed, more advanced systems keep the thread
    alive waiting for tasks. That is beyond the scope of
    this example.
    """

    def __init__(self, levels: tuple[str, ...], location: str):
        self._levels = levels
        self._location = location

        self._begun: bool = False
        self._finished: bool = False

        # Creating a Thread object does not start the thread.
        # That requires the thread's `start` method to be called
        self.loading_thread = threading.Thread(target=self._load_levels)

        self._loaded_levels: dict[str, arcade.TileMap] = {}
        self._failed_levels: set[str] = set()
        self._current_level: str = ''

        # Locks are used to protect a thread from values
        # changing while its working.
        # The LevelLoader carefully uses only one lock.
        # This can be dangerous because you ask for the
        # lock while it is in use. If that happens the thread
        # will freeze forever.
        self._interaction_lock = threading.Lock()

    # An underscore at the start of a method is how
    # Python hints to treat things as private. In this
    # case, it means only LevelLoader should call `_load_levels`.
    def _load_levels(self):
        for level in self._levels:
            with self._interaction_lock:
                self._current_level = level
            time.sleep(ARTIFICIAL_DELAY) # Don't include in actual implementations

            # With this simple implementation if the thread throws an error
            # it simple dies so we catch the only major error we might face
            try:
                path = f'{self._location}{level}.json'
                tilemap = arcade.load_tilemap(path, lazy=True)
            except FileNotFoundError:
                print(f"{level} doesn't exist. It will be skipped")
                with self._interaction_lock:
                    self._failed_levels.add(level)
                continue

            with self._interaction_lock:
                self._loaded_levels[level] = tilemap

        with self._interaction_lock:
            self._finished = True

    def start_loading_levels(self):
        with self._interaction_lock:
            if not self._begun:
                self.loading_thread.start()
                self._begun = True

    @property
    def current_level(self) -> str:
        with self._interaction_lock:
            return self._current_level

    @property
    def begun(self):
        with self._interaction_lock:
            return self._begun

    @property
    def finished(self):
        with self._interaction_lock:
            return self._finished

    def is_level_loaded(self, level: str) -> bool:
        with self._interaction_lock:
            return level in self._loaded_levels

    def did_level_fail(self, level: str) -> bool:
        with self._interaction_lock:
            return level in self._failed_levels

    def get_level(self, level: str) -> arcade.TileMap | None:
        with self._interaction_lock:
            return self._loaded_levels.get(level, None)


class LevelRenderer:
    """
    This is a small utility class for drawing the levels while they load.
    """

    def __init__(
            self,
            level: str,
            level_loader: LevelLoader,
            location: arcade.types.Point2,
            size: tuple[int, int]
        ):
        self.level_name = level
        self.loader = level_loader

        self.location = location
        self.size = size

        self.camera: arcade.Camera2D = arcade.Camera2D(
            arcade.XYWH(self.location[0], self.location[1], self.size[0], self.size[1])
        )
        self.level: arcade.TileMap | None = None
        self.level_text: arcade.Text = arcade.Text(
            level,
            self.camera.position.x,
            self.camera.position.y,
            anchor_x='center',
            anchor_y='center'
        )

    def update(self):
        if self.level is None and self.loader.is_level_loaded(self.level_name):
            self.level = self.loader.get_level(self.level_name)

    def draw(self):
        with self.camera.activate():
            if self.level is not None:
                for spritelist in self.level.sprite_lists.values():
                    spritelist.draw()
            self.level_text.draw()

        if self.level is not None:
            color = GREEN
        elif self.loader.did_level_fail(self.level_name):
            color = RED
        elif self.loader.current_level == self.level_name:
            color = BLUE
        else:
            color = WHITE

        arcade.draw_rect_outline(self.camera.viewport, color, 3)

    def point_in_area(self, x, y):
        return self.camera.viewport.point_in_rect((x, y))

    def drag(self, dx, dy):
        pos = self.camera.position
        self.camera.position = pos.x - dx / self.camera.zoom, pos.y - dy / self.camera.zoom

    def scroll(self, scroll):
        self.camera.zoom = max(0.1, min(10, self.camera.zoom + scroll / 10))


class GameView(arcade.View):

    def __init__(self, window = None, background_color = None):
        super().__init__(window, background_color)
        self.level_loader = LevelLoader(LEVELS, LEVEL_LOCATION)
        self.level_renderers: list[LevelRenderer] = []

        for idx, level in enumerate(LEVELS):
            row = idx // COLUMN_COUNT
            column = idx % COLUMN_COUNT
            pos = (1 + column) / 5 * self.width, (3 - row) / 4 * self.height
            self.level_renderers.append(
                LevelRenderer(level, self.level_loader, pos, LEVEL_RENDERER_SIZE)
            )

        self.loading_sprite = arcade.SpriteSolidColor(
            64,
            64,
            self.center_x,
            200,
            WHITE
        )

        self.dragging = None

    def on_show_view(self):
        self.level_loader.start_loading_levels()

    def on_update(self, delta_time):
        # This sprite will spin one revolution per second. Even when loading levels this
        # won't freeze thanks to the threaded loading
        self.loading_sprite.angle = (360 * self.window.time) % 360
        for renderer in self.level_renderers:
            renderer.update()

        if self.dragging is not None:
            self.window.set_mouse_cursor(self.window.get_system_mouse_cursor(self.window.CURSOR_SIZE))
        else:
            self.window.set_mouse_cursor(None)

    def on_draw(self):
        self.clear()
        arcade.draw_sprite(self.loading_sprite)
        for renderer in self.level_renderers:
            renderer.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for renderer in self.level_renderers:
            if renderer.point_in_area(x, y):
                self.dragging = renderer
                break

    def on_mouse_release(self, x, y, button, modifiers):
        self.dragging = None

    def on_mouse_drag(self, x, y, dx, dy, _buttons, _modifiers):
        if self.dragging is not None:
            self.dragging.drag(dx, dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.dragging is not None:
            self.dragging.scroll(scroll_y)
            return
        for renderer in self.level_renderers:
            if renderer.point_in_area(x, y):
                renderer.scroll(scroll_y)
                break


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
