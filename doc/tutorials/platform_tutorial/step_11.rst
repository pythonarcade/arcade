.. _platformer_part_eleven:

Step 11 - Using a Scene
-----------------------

So far in our game, we have three SpriteLists. One for our player, one for our walls(ground and boxes),
and one for our coins. This is still manageable, but whatabout as our game grows? You can probably imagine
a game could end up with hundreds of SpriteLists. Using just our current approach, we would have to keep track
of variables for each one, and ensure we're drawing them in the proper order.

Arcade provides a better way to handle this, with the :class:`arcade.Scene` class. This class will hold all of
our spritelists for us, allow us to create new ones, change around the order they get drawn in, and more. In
later chapters we will we use a special function to load a map from a map editor tool, and automatically create
a Scene based on the map.

At the end of this chapter, you will have the same result as before, but the code will be a bit different to use
the Scene object.

First-off, we can remove all of our SpriteList variables from ``__init__`` and replace them with on variable to hold
the scene object:

.. code-block::

    self.scene = None

Now at the very top of our ``setup`` function we can initialize the scene by doing:


.. code-block::

    self.scene = arcade.Scene()

Next, we will remove the line in ``setup`` that initializes our Player spritelist, that line looked like this:

.. code-block::

    self.player_list = arcade.SpriteList()

Then, instead of adding our player to the SpriteList using ``self.player_sprite.append()``. We will add the player
to the Scene directly:

.. code-block::

    self.player_sprite = arcade.Sprite(self.player_texture)
    self.player_sprite.center_x = 64
    self.player_sprite.center_y = 128
    self.scene.add_sprite("Player", self.player_sprite)

Let's analyze what happens when we do :func:`arcade.Scene.add_sprite`. The first parameter to it is a String,
this defines the layer name that we want to add a Sprite to. This can be an already existing layer or a new one.
If the layer already exists, the Sprite will be added to it, and if it doesn't, Scene will automatically create it.
Under the hood, a layer is just a SpriteList with a name. So when we specify ``Player`` as our Layer. Scene is creating
a new SpriteList, giving it that name, and then adding our Player Sprite to it.

Next we will replace our initialization of the wall and coin SpriteLists with these functions:

.. code-block::

    self.scene.add_sprite_list("Walls", use_spatial_hash=True)
    self.scene.add_sprite_list("Coins", use_spatial_hash=True)

Here we are taking a little bit different approach than we did for our ``Player`` layer. For our player, we just added
a Sprite directly. Here we are initialization new empty layers, named ``Walls`` and ``Coins``. The advantage to this approach
is that we can specify that this layer should use spatial hashing, like we specified for those SpriteLists before.

Now when we use the ``add_sprite`` function on these lists later, those Sprites will be added into these existing layers.

In order to add Sprites to these, let's modify the ``self.wall_list.append()`` functions within the for loops for placing our
walls and coins in the ``setup`` function. The only part we're actually changing of these loops is the last line where we
were adding it to the SpriteList, but I've included the loops so you can see where all it should be changed.

.. code-block::

    # Create the ground
    for x in range(0, 1250, 64):
        wall = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=TILE_SCALING)
        wall.center_x = x
        wall.center_y = 32
        self.scene.add_sprite("Walls", wall)

    # Putting Crates on the Ground
    coordinate_list = [[512, 96], [256, 96], [768, 96]]

    for coordinate in coordinate_li
        wall = arcade.Sprite(
            ":resources:images/tiles/boxCrate_double.png", scale=TILE_SCALING
        )
        wall.position = coordinate
        self.scene.add_sprite("Walls", wall)

    # Add coins to the world
    for x in range(128, 1250, 256):
        coin = arcade.Sprite(":resources:images/items/coinGold.png", scale=COIN_SCALING)
        coin.center_x = x
        coin.center_y = 96
        self.scene.add_sprite("Coins", coin)

The next thing we need to do is fix our Physics Engine. If you remember back in Chapter 4, we added
a physics engine and sent our Wall spritelist to in the ``walls`` parameter.

We'll need to modify that our PhysicsEnginePlatformer initialization to this:

.. code-block::

    self.physics_engine = arcade.PhysicsEnginePlatformer(
        self.player_sprite, walls=self.scene["Walls"], gravity_constant=GRAVITY
    )

This is mostly the same as before, but we are pulling the Walls SpriteList from our Scene. If you
are familiar with Python dictionaries, the :class:`arcade.Scene` class can be interacted with in
a very similar way. You can get any specific SpriteList within the scene by passing the name in
brackets to the scene.

We need to also change our :func:`arcade.check_for_collision_with_list` function in ``on_update`` that
we are using to get the coins we hit to use this new syntax.

.. code-block::

    coin_hit_list = arcade.check_for_collision_with_list(
        self.player_sprite, self.scene["Coins"]
    )

The last thing that we need to do is update our ``on_draw`` function. In here we will remove all our
SpriteLists draws, and replace them with one line drawing our Scene.

.. code-block::

    self.scene.draw()

.. note::

    Make sure to keep this after our world camera is activated and before our GUI camera is activated.
    If you draw the scene while the GUI camera is activated, the centering on the player and scrolling
    will not work.

Source Code
~~~~~~~~~~~

.. literalinclude:: ../../../arcade/examples/platform_tutorial/11_scene.py
    :caption: Using a Scene
    :linenos:
    :emphasize-lines: 39-40, 60, 67, 69-70, 78, 90, 97, 106-108, 149-151

Run This Chapter
~~~~~~~~~~~~~~~~

.. code-block::

  python -m arcade.examples.platform_tutorial.11_scene
