.. _resource_handles:

Resource Handles
================

Arcade supports resource handles to make loading assets easier.

Each resource handle is a shorthand prefix for a folder or series of
folders. When loading assets, they resource hanldes look like this:

.. code-block:: python

   ":handle_name_here:/folder/filename.png"

.. list-table:: Arcade's Default Resource Handles
   :header-rows: 1

   * - Handle
     - String Prefix
     - Contents
   * - assets
     - ``":assets:"``
     - Built-in images, sounds and other miscellaneous asset
   * - system
     - ``":system:``
     - System resources like shaders, fonts and default gui assets
   * - resources
     - ``:resources:``
     - Includes ``:system:`` and ``:assets:``  directories

.. _resource_handles-using:

Using Resource Handles
----------------------

.. _resource-handles-how-use:

How Do I Use Resource Handles?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The most common way is creating a :py:class:`~arcade.Sprite` like this:

.. code-block:: python

   SPRITE_SCALE = 0.5
   FEMALE_PERSON_IDLE = ":assets:images/animated_characters/female_person/femalePerson_idle.png"

   my_sprite = arcade.Sprite(FEMALE_PERSON_IDLE, SPRITE_SCALE)

This syntax is like easy to understand despite being long. As mentioned
above, the ``:assets:`` at the start of the string resembles the way a
folder or Windows drive can be used because it is the same sort of symbol:
a way to shorten one or more folders.

You will see the syntax above in most examples throughout the following:

* Much of this page
* Arcade's :ref:`tutorials <main-page-tutorials>`
* The ref:`example-code`.

To learn more about resource handles, including shorter syntax, keep reading.
Otherwise, you can jump the links above if you want to try running code sooner.

.. _resource-handles-when-where:

When & Where Can I Use Resource Handles?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can use a resource handle prefix anywhere an Arcade feature:

* takes a a string as a path

* does not warn against it like the :ref:`resource_handles-adding` section
  below

Most loading code in the areas below accepts a resource handle:

  * the :ref:`example-code`
  * the :ref:`tutorials <main-page-tutorials>`

What Doesn't Allow Resource Handles?
""""""""""""""""""""""""""""""""""""

If a function or object does not accept a resource handle prefix,
it is probably one of the following:

* a feature from another library which Arcade uses such as pyglet
* a problem you should report so we can fix it

If you're unsure, it's always okay to :ref:`ask for help <how-to-get-help>`.


.. _resource_handles-adding:

Adding Your Own Resource Handles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. TODO: intersphinx this link
.. _py_file_dunder: https://docs.python.org/3/reference/import.html#file__

You may want to define your own resource handles for various reasons.

The :py:func:`arcade.resources.add_resource_handle` function allows you
to do this. However, this function requires you to first find the absolute
path of the folder you would like to add.


What's An Absolute Path?
""""""""""""""""""""""""

When describing files on a computer, there are two ways
of describing them:

* **Relative** to something else, like "the Documents folder in my
  home directory"
* **Absolute**, which is relative to a drive or absolute
  'root' of the file system

Although you could write thiso out manually or use Python's oldest
file system tools, doing so can somewhat painful:

.. list-table:: Absolute vs Relative Examples
   :header-rows: 1

   * - Meaning
     - Relative Version
     - Absolute

   * - User Documents (Windows)
     - ``"%userprofile%\Documents"``
     - ``"C:\Users\YourAccountName\Documents"``

   * - User Documents (Everything Else)
     - ``"~/Documents"``
     - ``"/home/YourAccountName/Documents/"``


Adding your New Resource Handle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For the meantime, we'll stick to a simple example.

Pick a name for your handle. In the example code below, we'll:

* Use ``"my_resources"`` as the name
* Access files and folders inside for the folder by making sure each
  string starts with ``":my_resources:"``


Adding the Handle
"""""""""""""""""

.. TODO: synced tab plugins here? People on Win32 might get scared of forward slash *NIX style paths

.. code-block:: python

    arcade.resources.add_resource_handle("my_resources", "/home/users/username/my_game/my_res_folder")

.. note::

    The ``add_resource_handle`` function must be given an **absolute** path.

Then, you can use resources from your handle:

.. code-block:: python

    self.texture = arcade.load_texture(":my_resources:images/characters/my_character.png")

Despite needing an absolute path, you can use Python's ``Path.resolve()`` to resolve a relative path:

.. code-block:: python

    from pathlib import Path
    ...
    arcade.resources.add_resource_handle("my_resources", Path("assets/my_res_folder").resolve())


To learn more about finding your current directory, you may want to
define this at the top-level ``__init__.py`` in your project:

.. _resource_handles-adding-multiple:

Adding Multiple Directories to a Resource Handle
------------------------------------------------

You can also add multiple directories to a single resource handler:

.. code-block:: python

    # Adding multiple resources folders to the same resource handler:
    arcade.resources.add_resource_handle("my_resources", "/home/users/username/my_game/my_first_res_folder/")
    arcade.resources.add_resource_handle("my_resources", "/home/users/username/my_game/my_second_res_folder/")

When multiple directories are added to a single resource handler, Arcade will search through the added directories until
it locates the requested resource. Here, Arcade will start it's search in the last added directory first, in this case
``my_second_res_folder``. If the requested resource is not present within ``my_second_res_folder`` it will then move
onto the directories added before it, in this case, ``my_first_res_dir``.

.. important:: These **must** be absolute paths!

.. _resource_handles-cleaner-pathlib:

Cleaner Code with Pathlib
-------------------------

Python's built-in :py:mod:`pathlib` is the newest and
friendliest way to navigate files and folders on a computer.


Finding your Project Folder
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first thing you'll want to do is find your resources folder.

Arcade places this in the ``__init__.py`` file of its
``arcade.resources`` module. To make things easier, we'll use the
same structure here.


Import the Path Class Before Arcade
"""""""""""""""""""""""""""""""""""

To use :py:mod:`pathlib`, you usually only need to import
py:class:`~pathlib.Path` from it.

Since Python developers usually import built-ins before add-on
libraries like Arcade, we'll do the same here:

.. code-block:: python
   :lineno-start: 1
   :emphasize-lines: 1,1

   from pathlib import Path # <-- put the line here above Arcade
   import arcade


.. tip:: Following this import order makes your code more readable!

         This is important since you might:

         * :ref:`Ask someone else for help <how-to-get-help>`
         * Try to read your code months or years later


That's why we'll use the following to make this easier:

#. The ``__file__`` variable Python automatically creates in every file
#. The following methods and properties on :py:class:`pathlib.Path`: ``resolve()`` to get the absolute path, and
   ``parent`` to get the folder a file is in

First, we'll find the absolute path the ``__file__`` we're in:

.. code-block:: python
   :lineno-start: 1
   :emphasize-lines: 4,5

   from pathlib import Path
   import arcade

   # Create a Path for this file and make it absolute
   THIS_FILE = Path(__file__).resolve()

Next, we'll get the parent folder:

.. code-block:: python
   :lineno-start: 1
   :emphasize-lines: 7,8

   from pathlib import Path
   import arcade

   # Create a Path for this file and make it absolute
   THIS_FILE = Path(__file__).resolve()

   # Get the folder the __file__ is in
   PARENT_FOLDER = THIS_FILE.parent

You can now p

For example, imagine a game with multiple characters. Each has a folder with
their own sprites inside. Since the :py:func:`arcade.resources.resolve` function
returns a :py:class:`~pathlib.Path` object, you can resolve the folder for a
character once, then write shorter code using :py:class:`~pathlib.Path` slash
syntax:


.. code-block:: python

   SPRITE_SCALE = 0.5
   ANN_TEXTURE_PATH = arcade.resources.resolve(":assets:images/animated_characters/female_person/")

   my_sprite = arcade.Sprite(ANN_TEXTURE_PATH / "femalePerson_idle.png" , SPRITE_SCALE)



This is a complicated topic. For getting started quickly, you can
do the following.


More on How Resource Handles Work
---------------------------------

A resource handle is the name of a list of folders on disk.

Arcade resolves paths prefixed with a resource handle by starting at the
end of the list and working backwards. For each folder, it will try to do
the following:

1. Check if the file exists in that directory
2. If it does, return a :py:class:`pathlib.Path` object for it
3. It it does not, continue to the next directory

This behavior allows you to add, extend, and even override search
locations when loading files.

For anything imported from pyglet.

Implementation Details
^^^^^^^^^^^^^^^^^^^^^^

The handles are stored as a :py:class:`dict` inside ``arcade.resources.handles``.

* Each resource handle's name is a :py:class:`str` used to look up a :py:class:`list`
  of :py:class:`pathlib.Path` objects
* Each :py:class:`~pathlib.Path` refers to a directory on disk and supports


.. _resource_handles_one_file_builds:

Resources Handles and PyInstaller/Nuitka one-file builds
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
we can use the ``__file__`` variable to locate temporary folder's location.

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
    ``./`` will be interpreted to the location of the executable and not the temporary location your application is
    unbundled to.

