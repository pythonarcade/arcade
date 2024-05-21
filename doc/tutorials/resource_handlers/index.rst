.. _resource_handlers:

Adding Your Own Resource Handlers
=================================

Arcade provides a convenient way to locate asset through it's resource handlers. Arcade already has a number of
Built-In sprites, images and other resources available for use inside the ``:resources:`` handler, which you
may already be familiar with:

.. code-block:: python

   my_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", SPRITE_SCALE)


Arcade also allows the ability to register additional resources handlers. This is helpful when you want to include
your own resource folders for your project.

Basic Usage
-----------

You can register a new resource handler by using ``arcade.resources.add_resource_handler(handle: str, path: Union[str, Path])``:

.. code-block:: python

    arcade.resources.add_resource_handler("my_resources", "/home/users/username/my_game/my_res_folder")

.. note::

    The ``add_resource_handler`` function must be given an **absolute** path.

Then, you can use resources from your handler:

.. code-block:: python

    self.texture = arcade.load_texture(":my_resources:images/characters/my_character.png")

Despite needing an absolute path, you can use Python's ``os.path.resolve()`` to resolve a relative path:

.. code-block:: python

    from pathlib import Path
    ...
    arcade.resources.add_resource_handler("my_resources", Path("assets/my_res_folder"))

Adding Multiple Directories to a Resource Handler
-------------------------------------------------

You can also add multiple directories to a single resource handler:

.. code-block:: python

    # Adding multiple resources folders to the same resource handler:
    arcade.resources.add_resource_handler("my_resources", "/home/users/username/my_game/my_first_res_folder/")
    arcade.resources.add_resource_handler("my_resources", "/home/users/username/my_game/my_second_res_folder/")

In this case, Arcade will search for a requested resources through each of the added directories, starting with the last
added first.

.. _resource_handlers_one_file_builds:
Resources Handlers and PyInstaller/Nuitka one-file builds
---------------------------------------------------------

When distributing your file as a one-file, standalone build with either Nuitka or PyInstaller you will need to specify
relative paths differently to ensure that your distributed code can correctly locate your resource folder(s) on other
people's computers.

With one-file builds for both Nuitka and PyInstaller, the created executable is a bundled file that contains everything
that is needed to run your program, this includes all your `.py` files and the the data folders you specified in the
build command.

When the executable is ran, the files and folders are unbundled and placed inside a temporary location, (on Window's
this is normally ``C:\Users\UserName\AppData\Local\Temp``). This includes an exact copy of your data directory and it is
from here that your application is ran from. To ensure that the running executable correctly finds this data directory,
we can use the ``__file__`` dunder variable to locate temporary folder's location.

.. code-block:: Python

    asset_dir = os.path.join(Path(__file__).parent.resolve(), "assets")
    arcade.resources.add_resource_handle("assets", asset_dir)

Here ``__file__``, will either resolve to the temporary folder location or file which it is in when running your game
as a Python program: ``python mygame.py``.

.. note::

    ``sys.argv[0]`` is not the same as ``__file__``. ``sys.argv[0]`` will point to the original executable's location
    and not the temporary folders location. ``__file__`` is a special python dunder variable that contains the absolute
    file location from which a Python module was loaded from.

.. warning::

    Do not use a ``./`` (single dot) to specify the relative location (even when you use ``Path.resolve()``). The
    ``./`` will be interpreted to the location of the executable and not the temporary location your executable your
    application is unbundled too.