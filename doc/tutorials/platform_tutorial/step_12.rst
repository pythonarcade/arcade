.. _platformer_part_twelve:

Step 12 - Loading a Map From a Map Editor
-----------------------------------------

In this chapter we will start using a map editor called `Tiled`_.
Tiled is a popular 2D map editor, it can be used with any game engine, but Arcade has specific integrations
for working with Tiled.

.. _Tiled: https://www.mapeditor.org/

We'll explore how to load maps from Tiled in this tutorial using Arcade's built-in :class:`arcade.TileMap` class
using some maps from the built-in resources that Arcade comes with. We won't cover actually building a map
in Tiled this tutorial, but if you want to learn more about Tiled check out the resources below:

* Download Tiled: https://www.mapeditor.org/
* Tiled's Documentation: https://doc.mapeditor.org/en/stable/

You won't actually need Tiled to continue following this tutorial. We will be using all pre-built maps included
with Arcade. However if you want to experiment with your own maps or changing things, I recommend getting Tiled
and getting familiar with it, it is a really useful tool for 2D Game Development.

To start off with, we're going to remove a bunch of code. Namely we'll remove the creation of our ground, boxes,
and coin sprites(We'll leave the player one). Go ahead and remove the following blocks of code from the ``setup`` function.

.. code-block::

    self.scene.add_sprite_list("Walls", use_spatial_hash=True)
    self.scene.add_sprite_list("Coins", use_spatial_hash=True)

    for x in range(0, 1250, 64):
        wall = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=TILE_SCALING)
        wall.center_x = x
        wall.center_y = 32
        self.scene.add_sprite("Walls", wall)

    coordinate_list = [[512, 96], [256, 96], [768, 96]]

    for coordinate in coordinate_list:
        wall = arcade.Sprite(
            ":resources:images/tiles/boxCrate_double.png", scale=TILE_SCALING
        )
        wall.position = coordinate
        self.scene.add_sprite("Walls", wall)

    for x in range(128, 1250, 256):
        coin = arcade.Sprite(":resources:images/items/coinGold.png", scale=COIN_SCALING)
        coin.center_x = x
        coin.center_y = 96
        self.scene.add_sprite("Coins", coin)

These things will now be handled by our map file automatically once we start loading it.

In order to load our map, we will first create a variable for it in ``__init__``:

.. code-block::

    self.tile_map = None

Next we will load our map in our ``setup`` function, and then create a Scene from it using
a built-in function Arcade provides. This will give us a drawable scene completely based off
of the map file automatically. This code will all go at the top of the ``setup`` function.

Make sure to replace the line that sets ``self.scene`` with the new one below.

.. code-block::

    layer_options = {
        "Platforms": {
            "use_spatial_hash": True
        }
    }

    self.tile_map = arcade.load_tilemap(
        ":resources:tiled_maps/map.json",
        scaling=TILE_SCALING,
        layer_options=layer_options
    )

    self.scene = arcade.Scene.from_tilemap(self.tile_map)

This code will load in our built-in Tiled Map and automatically build a Scene from it. The Scene
at this stage is ready for drawing and we don't need to do anything else to it(other than add our player).

.. note::

    What is ``layer_options`` and where are those values in it coming from?

    ``layer_options`` is a special dictionary that can be provided to the ``load_tilemap`` function. This will
    send special options for each layer into the map loader. In this example our map has a layer called
    ``Platforms``, and we want to enable spatial hashing on it. Much like we did for our ``wall`` SpriteList
    before. For more info on the layer options dictionary and the available keys, check out :class`arcade.TileMap`

At this point we only have one piece of code left to change. In switching to our new map, you may have noticed by
the ``layer_options`` dictionary that we now have a layer named ``Platforms``. Previously in our Scene we were calling
this layer ``Walls``. We'll need to go update that reference when we create our Physics Engine.

In the ``setup`` function update the Physics Engine creation to use the the new ``Platforms`` layer:

.. code-block:: 
    
    self.physics_engine = arcade.PhysicsEnginePlatformer(
        self.player_sprite, walls=self.scene["Platforms"], gravity_constant=GRAVITY
    )

Source Code
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/12_tiled.py
    :caption: Loading a Map From a Map Editor
    :linenos:
    :emphasize-lines: 39-40, 63-73, 90