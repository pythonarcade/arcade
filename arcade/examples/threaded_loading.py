"""
Load level data in the background with interactive previews.

Level preview borders will turn green when their data loads:

1. Pan the camera by clicking and dragging
2. Zoom in and out by scrolling up or down

Loading data during gameplay always risks slowdowns. These risks grow
grow with number, size, and loading complexity of files. Some games
avoid the problem by using non-interactive loading screens. This example
uses a different approach.

Background loading works if a game has enough RAM and CPU cycles to
run light features while loading. These can be the UI or menus, or even
gameplay light enough to avoid interfering with the loading thread. For
example, players can handle inventory or communication while data loads.

Although Python's threading module has many pitfalls, we'll avoid them
by keeping things simple:

1. There is only one background loader thread
2. The loader thread will load each map in order, one after another
3. If a map loads successfully, the UI an interactive preview

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.threaded_loading
"""
from __future__ import annotations

import sys
import time

# Python's threading module has proven tools for working with threads, and
# veteran developers may want to explore 3.13's new 'No-GIL' concurrency.
import threading

import arcade
from arcade.color import RED, GREEN, BLUE, WHITE
from arcade.math import clamp

# Window size and title
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = 'Threaded Tilemap Loading'

# We'll simulate loading large files by adding a loading delay to
# each map we load. You can omit the delay in your own projects.
ARTIFICIAL_DELAY = 1


# The resource handle prefix to load map files from
LEVEL_LOCATION = ':assets:tiled_maps/'
# Level filenames in the resource folder
LEVELS = (
    'test_map_1.json',
    'test_map_2.json',
    'test_map_3.json',
    'test_map_4.json',  # Doesn't exist so we can simulate failed reads
    'test_map_5.json',  # Intentionally empty file
    'test_map_6.json',
    'test_map_7.json',
)

# Rendering layout controls
COLUMN_COUNT = 4
LEVEL_RENDERER_SIZE = WINDOW_WIDTH // 5 - 10, WINDOW_HEIGHT // 5 - 10


class LevelLoader:
    """Wrap a loader thread which runs level loading in the background.

    IMPORTANT: NEVER call graphics code from threads! They break OpenGL!

    It's common to group threading tasks into manager objects which track
    and coordinate them. Advanced thread managers often keep idle threads
    'alive' to re-use when needed. These complex techniques are beyond the
    scope of this tutorial.
    """

    def __init__(self, levels: tuple[str, ...], location: str):
        self._levels = levels
        self._location = location

        self._begun: bool = False
        self._finished: bool = False

        # Threads do not start until their `start` method is called.
        self.loading_thread = threading.Thread(target=self._load_levels)

        self._loaded_levels: dict[str, arcade.TileMap] = {}
        self._failed_levels: set[str] = set()
        self._current_level: str = ''

        # Avoid the difficulties of coordinating threads without
        # freezing by using one loading thread with a one lock.
        self._interaction_lock = threading.Lock()

    # An underscore at the start of a name is how a developer tells
    # others to treat things as private. Here, it means that only
    # LevelLoader should ever call `_load_levels` directly.
    def _load_levels(self):
        for level in self._levels:
            with self._interaction_lock:
                self._current_level = level

            time.sleep(ARTIFICIAL_DELAY)  # "Slow" down (delete this line before use)

            # Since unhandled exceptions "kill" threads, we catch the only major
            # exception we expect. Level 4 is intentionally missing to test cases
            # such as this one when building map loading code.
            try:
                path = f'{self._location}{level}'
                tilemap = arcade.load_tilemap(path, lazy=True)
            except FileNotFoundError:
                print(f"ERROR: {level} doesn't exist, skipping!", file=sys.stderr)
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
    Draws previews of loaded data and colored borders to show status.
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
        x, y = location
        self.camera: arcade.Camera2D = arcade.Camera2D(
            arcade.XYWH(x, y, size[0], size[1])
        )
        camera_x, camera_y = self.camera.position
        self.level: arcade.TileMap | None = None
        self.level_text: arcade.Text = arcade.Text(
            level,
            camera_x, camera_y,
            anchor_x='center',
            anchor_y='center'
        )

    def update(self):
        level = self.level
        loader = self.loader
        if not level and loader.is_level_loaded(self.level_name):
            self.level = self.loader.get_level(self.level_name)

    def draw(self):
        # Activate the camera to render into its viewport rectangle
        with self.camera.activate():
            if self.level:
                for spritelist in self.level.sprite_lists.values():
                    spritelist.draw()
            self.level_text.draw()

        # Choose a color based on the load status
        if self.level is not None:
            color = GREEN
        elif self.loader.did_level_fail(self.level_name):
            color = RED
        elif self.loader.current_level == self.level_name:
            color = BLUE
        else:
            color = WHITE

        # Draw the outline over any thumbnail
        arcade.draw_rect_outline(self.camera.viewport, color, 3)

    def point_in_area(self, x, y):
        return self.camera.viewport.point_in_rect((x, y))

    def drag(self, dx, dy):
        # Store a few values locally to make the math easier to read
        camera = self.camera
        x, y = camera.position
        zoom = camera.zoom

        # Move the camera while accounting for zoom
        camera.position = x - dx / zoom, y - dy / zoom

    def scroll(self, scroll):
        camera = self.camera
        zoom = camera.zoom
        camera.zoom = clamp(zoom + scroll / 10, 0.1, 10)


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
            self.window.set_mouse_cursor(
                self.window.get_system_mouse_cursor(self.window.CURSOR_SIZE))
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
