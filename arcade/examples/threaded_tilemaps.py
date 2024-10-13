"""
Threaded Tilemaps

Using the threading module to load tilemaps without stopping
Arcade's event loop from running.

This is an advanced topic that can easily cause confusing and hard
to solve bugs.

By default mutli-threading in this way does not speed up your program.
In Arcade this style of mutli-threading is used to keep the eventloop running.

You may see some performance improvements if you thread file IO as this
process often hangs waiting for your computer to fetch the data from storage.

If you have a computation bound issue such as calculating many numbers
you won't see a performace improvement. However,
it can still be useful if you don't need the info right away.

An example where it may still be useful:
If you have many units in your game who are trying to calculate their path through
a very large map you will get lag spikes everytime a unit has to find a new path.
Since the unit will take time to reach their final location you have time to find
the optimal path on a thread. Protecting you from lag-spikes.

If Python and Arcade are installed, this example can be run from
the command line with:
python -m arcade.examples.threaded_tilemaps
"""
from __future__ import annotations

from pathlib import Path
from threading import Thread, Lock, Event
from time import sleep
from typing import Callable

import arcade
from arcade.gui.events import UIOnActionEvent
from arcade.resources import resolve
from arcade.tilemap import TileMap
from arcade.gui import (
    UIManager,
    UIButtonRow,
    UIBoxLayout,
    UIFlatButton,
    UIAnchorLayout
)

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Tilemap loading using threading"

LEVEL_VIEWER_RECT = arcade.XYWH(
    WINDOW_WIDTH * 0.5, WINDOW_HEIGHT * 0.25,
    WINDOW_WIDTH * 0.75, WINDOW_HEIGHT * 0.25
)

BACKGROUND_COLOR = arcade.color.DARK_GRAY
MAX_ROW_BUTTONS = 10
MAX_TIMEOUT = 1  # Second(s) to timeout after

class MapLoader:
    """
    The class that will load all of the tilemaps available.

    It uses the convention of _ prefixed methods to mark methods
    that should be called off of the main thread.

    Objects like SpriteLists, TextureAtlases, and TiledMaps by default
    interact with the GPU. This isn't possible when off the main thread.
    It will call esoteric errors if you attempt to. Make sure you use the lazy
    loading options on threads. This prevents the GPU interactions from happening
    untill strictly neccisary.

    In this example we don't allow for any manipulation of the tilemap input arguments,
    but there are multiple ways to fix this. Either pass them in at init like with the
    `tilemap_folder`, or add it as extra args to `
    """

    def __init__(self, tilemap_folder: Path):
        self.tilemap_folder: Path = tilemap_folder

         # The thread that will load our tilemaps
        self._loading_thread: Thread = None

        # The paths to the tilemaps by name
        self._tilemap_paths: dict[str, Path] = {}

        # A dict of names to tilemaps that we use to get the loaded levels
        self._tilemaps: dict[str, TileMap] = {}

        # The name of the tilemap the thread is currently loading
        self._currently_loading_tilemap: str = None

        # Events can be waited upon until another thread triggers it.
        # We use this to pause this thread until a level needs loading
        self._load_tiled_map: Event = Event()

        # A flag to track if all levels are loaded
        self._finished_loading: bool = False

        # A flag to kill the thread early incase the window is closed
        self._culled: bool = False

        # Locks can be used to protect resources. When a thread uses `with <lock>`
        # It will wait until any other threads are done with it.
        # You must be VERY careful to not try ask for a lock when you are already
        # locking as this can cause a thread to freeze. There are solutions
        # to this issue in the threading module.
        # If you are careful you can use less locks, but having one per value/task
        # is much safer.
        self._tilemap_name_lock: Lock = Lock()
        self._tilemap_dict_lock: Lock = Lock()
        self._loading_tilemap_lock: Lock = Lock()
        self._finished_lock: Lock = Lock()
        self._culled_lock: Lock = Lock()

    # Methods called by the main thread

    @property
    def tilemap_paths(self) -> tuple[Path, ...]:
        with self._tilemap_name_lock:
            return tuple(self._tilemap_paths.values())

    @property
    def tilemap_names(self) -> tuple[str, ...]:
        with self._tilemap_name_lock:
            return tuple(self._tilemap_paths.keys())

    @property
    def available(self) -> bool:
        with self._loading_tilemap_lock:
            return self._currently_loading_tilemap is None

    @property
    def culled(self) -> bool:
        with self._culled_lock:
            return self._culled

    @property
    def loading_level(self) -> str | None:
        with self._loading_tilemap_lock:
            return self._currently_loading_tilemap

    def load_level(self, name: str) -> bool:
        if not self.available:
            return False

        with self._tilemap_dict_lock:
            if name in self._tilemaps:
                return False

        with self._loading_tilemap_lock:
            self._currently_loading_tilemap = name

        self._load_tiled_map.set()
        return True

    def is_level_loaded(self, name: str) -> bool:
        with self._tilemap_dict_lock:
            return name in self._tilemaps

    def is_level_loading(self, name: str) -> bool:
        with self._loading_tilemap_lock:
            return name == self._currently_loading_tilemap

    def get_level(self, name: str) -> TileMap | None:
        with self._tilemap_dict_lock:
            return self._tilemaps.get(name, None)

    def create_thread(self):
        """
        Creating the thread does not start it, but when doing multi-threading
        it is important to know clearly what objects exsist when.

        Importantly when we create the thread we do NOT call the target method.
        The thread will call this method when we tell it too.

        The args arguments allows us to pass in values that will be used as arguments
        for the thread's target function. It has to be a Sequence even if you have
        only one value. For safety it is advisable to use tuples rather than lists.

        We don't need to pass in `self` because it will behave the same as when you
        call an object's method.
        """
        self._loading_thread = Thread(
            target=self._load_tiledmaps,
            args=(self.tilemap_folder,)
        )

    def start_thread(self):
        """
        Starting the thread creates the actual thread object. This has a cost associated with it,
        and should be done infrequently. This is why MapLoader uses only one thread and has it
        wait for instructions from the main thread.
        """
        if self._loading_thread is None:
            raise ValueError("create_thread has not yet been called and there is not thread to start")

        try:
            self._loading_thread.start()
        except RuntimeError:
            raise RuntimeError('start_thread was called for a second time before create_thread was recalled')

    def cull_thread(self):
        """
        When the window closes we have to also kill this thread.
        For some applications you can instead make the thread a `daemon`
        which gets closed as soon as the main thread is finished.

        If you are doing any sort of file IO this can be dangerous, and
        corrupt your data so we have to go through this method instead.
        """
        if self._loading_thread is None:
            raise ValueError("create_thread has not yet been called so there is no thread to cull")

        with self._culled_lock:
            self._culled = True

        # We have to tell the thread to load a level as that is where
        # the thread is waiting. In a smarter version you might have a
        # more generic `continue event`
        self._load_tiled_map.set()

    # Methods called by the loading thread

    def _load_tiledmaps(self, tilemap_folder: Path):
        """
        The heart of the thread. When this method finished the thread will automatically
        close itself. The thread has access to global values just like the main thread.
        This can cause confusing issues if you aren't careful.

        Functions, Objects, and values that are safe to use with mutli-threading are
        often called `atomic`

        We could have used `self.tilemap_folder` rather than passing it in, but
        by passing it in as an argument, we don't have to worry about the value
        changing. We still need to be careful of the folder being deleted or moved.
        """
        with self._finished_lock:
            self._finished_loading = False

        with self._tilemap_name_lock:
            # Get all the tiled_maps in the folder
            self._tilemap_paths = {
                path.stem: path for path in tilemap_folder.iterdir()
                if path.suffix == '.json'
            }

        # Loop forever so we can safely break using locks internally
        while True:
            cont = self._load_tiled_map.wait(timeout=MAX_TIMEOUT)
            self._load_tiled_map.clear()

            if not cont:
                try:
                    # This isn't very safe as there is no sort of lock
                    # around get_window, but it is the only way to validate
                    # that the window is still around in the case of a crash
                    arcade.get_window()
                except RuntimeError:
                    print('failed to get window, culling thread')
                    with self._culled_lock:
                        self._culled = True
                    break

            with self._culled_lock:
                # If the thread was culled then lets quit immediately
                if self._culled:
                    break

            # We force the thread to sleep an extra second because
            # this helps show off that the main thread isn't blocked.
            # You wouldn't want to add this in your own version.
            sleep(0)

            with self._loading_tilemap_lock:
                if self._currently_loading_tilemap is None:
                    continue
                name = self._currently_loading_tilemap

            tilemap = TileMap(name, lazy=True)
            with self._tilemap_dict_lock:
                self._tilemaps[name] = tilemap

            # If every tilemap has been loaded then the thread can be culled.
            # A smarter system could let the thread accept a new path to load from.
            with self._tilemap_dict_lock, self._tilemap_name_lock:
                    if self._tilemap_paths.keys == self._tilemaps.keys:
                        break

        with self._finished_lock:
            self._finished_loading = True


class LevelButtonRow(UIButtonRow):

    def __init__(self, level_names: tuple[str, ...], load_level_callback: Callable):
        super().__init__()
        print(level_names)
        self.levels = level_names
        self.callback = load_level_callback
        for name in self.levels:
            self.add_button(name)

    def on_action(self, event: UIOnActionEvent):
        self.callback(event.action)

class GameView(arcade.View):

    def __init__(self):
        super().__init__()
        self.gui_manager = UIManager()
        self.gui_anchor = None

        self.background_color = BACKGROUND_COLOR
        self.map_loader = MapLoader(resolve(":assets:tiled_maps"))
        self.level_names = ()

        self.gui_camera = arcade.Camera2D()
        self.level_camera = arcade.Camera2D(
            viewport=LEVEL_VIEWER_RECT
        )

    def on_window_close(self):
        # When the window closes we have to kill the thread as
        # it won't close naturally.
        self.map_loader.cull_thread()

    def try_load_level(self, level: str):
        succeded_loading = self.map_loader.load_level(level)

        if not succeded_loading:
            self.failed_to_load = True

    def setup(self):
        self.map_loader.create_thread()
        self.map_loader.start_thread()

        self.gui_manager.clear()
        self.gui_anchor = UIAnchorLayout(
            x = 0.5 * self.window.width,
            y = 0.75 * self.window.height,
            width = 0.75 * self.window.width,
            height = 0.5 * self.window.height
        )

    def reset(self):
        pass

    def get_levels(self):
        self.level_names = self.map_loader.tilemap_names
        if self.level_names:
            level_count = len(self.level_names)
            row_count = (level_count-1) // MAX_ROW_BUTTONS + 1
            for row in range(row_count + 1):
                self.gui_anchor.add(
                    LevelButtonRow(
                        self.level_names[row*MAX_ROW_BUTTONS:(row+1)*MAX_ROW_BUTTONS],
                        self.try_load_level
                    )
                )

    def on_draw(self):
        self.clear()

        with self.level_camera.activate():
            pass

        with self.gui_camera.activate():
            arcade.draw_rect_filled(LEVEL_VIEWER_RECT, arcade.color.WHITE)
            self.gui_manager.draw()

    def on_update(self, delta_time):
        if not self.level_names:
            self.get_levels()


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create and setup the GameView
    game = GameView()
    game.setup()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
