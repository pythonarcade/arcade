.. _Tiled Map Editor: https://www.mapeditor.org/

.. _platformer_part_nine:

Step 9 - Use a Map Editor
-------------------------

.. image:: use_tileset.png
    :width: 70%

Create a Map File
~~~~~~~~~~~~~~~~~

For this part, we'll restart with a new program. Instead of placing our tiles
by code, we'll use a map editor.

Download and install the `Tiled Map Editor`_. (Think about donating, as it is
a wonderful project.)

Open a new file with options similar to these:

* Orthogonal - This is a normal square-grid layout. It is the only version that
  Arcade supports very well at this time.
* Tile layer format - This selects how the data is stored inside the file. Any option works, but Base64
  zlib compressed is the smallest.
* Tile render order - Any of these should work. It simply specifies what order the tiles are
  added. Right-down has tiles added left->right and top->down.
* Map size - You can change this later, but this is your total grid size.
* Tile size - the size, in pixels, of your tiles. Your tiles all need to be the same size.
  Also, rendering works better if the tile size is a power of 2, such as
  16, 32, 64, 128, and 256.

.. image:: new_file.png
   :scale: 80%

.. Note::

   Arcade can only work with JSON maps from Tiled. TMX maps will not work. Make sure to save/export your maps accordingly.

Save it as ``map.json``.

Rename the layer "Platforms". We'll use layer names to load our data later. Eventually
you might have layers for:

* Platforms that you run into (or you can think of them as walls)
* Coins or objects to pick up
* Background objects that you don't interact with, but appear behind the player
* Foreground objects that you don't interact with, but appear in front of the player
* Insta-death blocks (like lava)
* Ladders

.. Note::

    Once you get multiple layers it is VERY easy to add items to the wrong
    layer.

.. image:: platforms.png
   :scale: 80%

Create a Tileset
~~~~~~~~~~~~~~~~

Before we can add anything to the layer we need to create a set of tiles.
This isn't as obvious or intuitive as it should be. To create a new tileset
click "New Tileset" in the window on the lower right:

.. image:: new_tileset.png
   :scale: 80%

Right now, Arcade only supports a "collection of images" for a tileset.
I find it convenient to embed the tileset in the map.

.. image:: new_tileset_02.png
   :scale: 80%

Once you create a new tile, the button to add tiles to the tileset is
hard to find. Click the wrench:

.. image:: new_tileset_03.png
   :scale: 80%

Then click the 'plus' and add in your tiles

.. image:: new_tileset_04.png
   :scale: 80%

Draw a Level
~~~~~~~~~~~~

At this point you should be able to "paint" a level. At the very least, put
in a floor and then see if you can get this program working. (Don't put
in a lot of time designing a level until you are sure you can get it to
load.)

We are able to load in the map file to a ``TileMap`` object, and then use that
object to create our scene. This will take all of the layers in the map and load
them in as SpriteLists, and set their draw orders in the scene to however they are
defined in the map file. You can access the SpriteLists directly the same way you do
with a normal scene. The SpriteLists are named according to the layer names from Tiled.

Test the Level
~~~~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/09_load_map.py
    :caption: Load a .json file from Tiled Map Editor
    :linenos:
    :emphasize-lines: 41-42, 69-84, 103-106

.. note::

    You can set the **background color** of the map by selecting "Map...Map Properties".
    Then click on the three dots to pull up a color picker.

    You can edit the **hitbox** of a tile to make ramps
    or platforms that only cover a portion of the rectangle in the grid.

    To edit the hitbox, use the polygon tool (only) and draw a polygon around
    the item. You can hold down "CTRL" when positioning a point to get the exact
    corner of an item.

    .. image:: collision_editor.png
       :scale: 20%

Source Code
~~~~~~~~~~~

* :ref:`09_load_map`
* :ref:`09_load_map_diff`