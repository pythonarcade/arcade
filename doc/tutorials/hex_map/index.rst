.. _hex_map_tutorial:

Working with Hexagonal Tilemaps
===============================

This tutorial covers how to load and display hexagonal tilemaps in Arcade using
the `Tiled`_ map editor and Arcade's :mod:`arcade.hexagon` module.

You don't need to understand all the math behind hexagonal grids to follow this
tutorial, but if you're building something with hexes,
`Red Blob Games' guide to hexagonal grids <https://www.redblobgames.com/grids/hexagons/>`_
is an invaluable resource for understanding the coordinate systems, algorithms, and
geometry involved.

.. _Tiled: https://www.mapeditor.org/

Hexagonal Coordinate Systems
-----------------------------

Hexagonal grids use a different coordinate system than square grids. Arcade's
:class:`~arcade.hexagon.HexTile` class uses **cube coordinates** (q, r, s) where
``q + r + s = 0`` always holds true. This constraint means you only need two of the
three values to uniquely identify a hex, but keeping all three makes the math simpler.

.. code-block:: python

    from arcade.hexagon import HexTile

    # Create a hex tile at the origin
    origin = HexTile(0, 0, 0)

    # A neighbor one step in the q direction
    neighbor = HexTile(1, -1, 0)

    # Distance between two hexes
    dist = origin.distance_to(neighbor)  # 1

Cube coordinates are great for math, but map editors like Tiled use **offset
coordinates** (column, row). Arcade handles the conversion automatically when
loading maps, but you can also convert manually:

.. code-block:: python

    from arcade.hexagon import HexTile, OffsetCoord

    # Convert from offset to cube
    offset = OffsetCoord(col=3, row=2)
    cube = offset.to_cube("even-r")

    # Convert back
    offset_again = cube.to_offset("even-r")

The offset system must match your map's configuration. Tiled hex maps typically
use ``"even-r"`` (staggered rows, even rows shifted right).

Hex Layout
----------

A :class:`~arcade.hexagon.Layout` defines how hex coordinates map to pixel positions
on screen. It contains three pieces of information:

1. **Orientation** -- pointy-top or flat-top hexagons
2. **Size** -- the size of each hexagon in pixels
3. **Origin** -- the pixel position of hex (0, 0, 0)

.. code-block:: python

    from pyglet.math import Vec2
    from arcade.hexagon import Layout, pointy_orientation, flat_orientation

    # Pointy-top hexagons (what Tiled uses)
    layout = Layout(
        orientation=pointy_orientation,
        size=Vec2(40.0, 40.0),
        origin=Vec2(0.0, 0.0),
    )

.. note::

    Tiled always uses **pointy-top** orientation for hexagonal maps.
    Use ``pointy_orientation`` when loading Tiled hex maps.

Computing the Hex Size from Tiled
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``size`` in a Layout is **not** the same as the tile width/height in Tiled.
For pointy-top hexagons, the conversion is:

.. code-block:: python

    import math

    # From your Tiled map properties
    tile_width = 120   # tilewidth in the .tmj file
    tile_height = 140  # tileheight in the .tmj file

    hex_size_x = tile_width / math.sqrt(3)
    hex_size_y = tile_height / 2

    layout = Layout(
        orientation=pointy_orientation,
        size=Vec2(hex_size_x, hex_size_y),
        origin=Vec2(0, 0),
    )

These values come from the relationship between a hexagon's size and its bounding
rectangle. See the `Red Blob Games size reference
<https://www.redblobgames.com/grids/hexagons/#size-and-spacing>`_ for the full
derivation.

Loading a Hex Map from Tiled
-----------------------------

Loading a hexagonal tilemap works just like loading a regular tilemap, with one
extra parameter: ``hex_layout``. This tells Arcade how to convert hex coordinates
to pixel positions.

Here is a complete example:

.. code-block:: python

    import math
    from pyglet.math import Vec2

    import arcade
    from arcade import hexagon

    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720


    class GameView(arcade.View):

        def __init__(self):
            super().__init__()
            self.tile_map: arcade.TileMap
            self.scene: arcade.Scene

        def reset(self):
            # Tiled always uses pointy-top orientation
            orientation = hexagon.pointy_orientation

            # Calculate hex size from the tile dimensions in your .tmj file
            hex_size_x = 120 / math.sqrt(3)
            hex_size_y = 140 / 2

            hex_layout = hexagon.Layout(
                orientation=orientation,
                size=Vec2(hex_size_x, hex_size_y),
                origin=Vec2(0, 0),
            )

            # Load the hex tilemap -- note the hex_layout parameter
            self.tile_map = arcade.load_tilemap(
                ":resources:tiled_maps/hex_map.tmj",
                hex_layout=hex_layout,
                use_spatial_hash=True,
            )

            # Create a Scene from the tilemap, just like a square map
            self.scene = arcade.Scene.from_tilemap(self.tile_map)

            self.background_color = arcade.color.BLACK

        def on_draw(self):
            self.clear()
            self.scene.draw()


    def main():
        window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, "Hex Map")
        game = GameView()
        window.show_view(game)
        game.reset()
        arcade.run()


    if __name__ == "__main__":
        main()

The key difference from a regular tilemap is the ``hex_layout`` parameter passed to
:func:`arcade.load_tilemap`. Without it, Arcade treats the map as a square grid.
With it, Arcade uses hex coordinate math to position each tile correctly.

Everything else -- creating a Scene, drawing, using layers -- works the same as
with square tilemaps. See :ref:`platformer_part_twelve` for the general tilemap
loading tutorial.

Working with Hex Tiles in Code
-------------------------------

The :class:`~arcade.hexagon.HexTile` class provides several useful operations:

**Neighbors and Distance**

.. code-block:: python

    tile = HexTile(2, -1, -1)

    # Get all 6 neighbors
    neighbors = tile.neighbors()

    # Get a specific neighbor by direction (0-5)
    north = tile.neighbor(0)

    # Distance between two hexes
    dist = tile.distance_to(HexTile(0, 0, 0))  # 2

**Rotation**

.. code-block:: python

    tile = HexTile(1, -3, 2)

    rotated_right = tile.rotate_right()  # HexTile(3, -2, -1)
    rotated_left = tile.rotate_left()    # HexTile(-2, -1, 3)

**Line Drawing**

.. code-block:: python

    from arcade.hexagon import line

    # Get all hexes on a line between two points
    path = line(HexTile(0, 0, 0), HexTile(3, -3, 0))

**Pixel Conversion**

.. code-block:: python

    from arcade.hexagon import hextile_to_pixel, pixel_to_hextile

    # Convert a hex to pixel coordinates
    pixel_pos = hextile_to_pixel(tile, layout)

    # Convert a mouse click back to hex coordinates
    hex_tile = pixel_to_hextile(Vec2(mouse_x, mouse_y), layout)
    snapped = round(hex_tile)  # Round to nearest hex

Creating a Hex Map in Tiled
-----------------------------

To create your own hexagonal map in Tiled:

1. Open Tiled and select **File > New > New Map**
2. Set **Map Orientation** to ``Hexagonal``
3. Set **Tile Render Order** to ``Right Down``
4. Set **Stagger Axis** to ``Y`` and **Stagger Index** to ``Odd``
5. Set your desired **Tile Width** and **Tile Height**
6. Set the **Hex Side Length** (this controls how "tall" the flat edges are)
7. Create your tileset and start painting

When loading the map in Arcade, make sure your Layout's ``size`` values match
the tile dimensions as shown in the `Computing the Hex Size from Tiled`_ section
above.

Full Example
------------

For a complete working example with camera controls (panning and zooming), see
the built-in hex map example:

.. code-block:: bash

    python -m arcade.examples.hex_map

Source: ``arcade/examples/hex_map.py``
