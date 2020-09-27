.. _bundle_into_redistributable:

Bundling a Game with PyInstaller
================================

.. note::

    You must have Arcade version 2.4.3 or greater and Pymunk 5.7.0 or greater
    for the instructions below to work.*

You've written your game using Arcade_ and it is a masterpiece! Congrats! Now
you want to share it with others. That usually means helping people install
Python, downloading the necessary modules, copying your code, and then getting
it all working. Sharing is not an easy task. Well, PyInstaller_ can change all
that!

PyInstaller_ is a tool for Python that lets you bundle up an entire Python
application into a one-file executable bundle that you can easily share.
Thankfully, it works great with Arcade_!

Bundling a Simple Arcade Script
-------------------------------

To demonstrate how PyInstaller works, we will:

* install PyInstaller
* create a simple example application that uses Arcade
* bundle the application into a one-file executable
* run the application

First, install PyInstaller into your environment with:

.. code-block:: bash

    pip install pyinstaller

Then create a file called ``myscript.py`` that contains the following:

.. code-block:: python

    import arcade
    arcade.open_window(400, 400, "My Script")
    arcade.start_render()
    arcade.draw_circle_filled(200, 200, 100, arcade.color.BLUE)
    arcade.finish_render()
    arcade.run()

Now, create a one-file executable bundle file by running PyInstaller:

.. code-block:: bash

    pyinstaller myscript.py --onefile

PyInstaller generates the executable that is a bundle of your game. It puts it in the ``dist\`` folder under your current working directory. Look for a
file named ``myscript.exe`` in ``dist\``. Run this and see the example application start up!

You can copy this file wherever you want on your computer and run it. Or, share it with others. Everything your
script needs is inside this executable file.

For simple games, this is all you need to know! But, if your game loads any kind of data files from disk, continue reading.

Handling Data Files
-------------------

When creating a bundle, PyInstaller first examines your project and automatically identifies nearly everything your project needs (a Python interpreter,
installed modules, etc). But, it can't automatically determine what data files your game is loading from disk (images, sounds,
maps). So, you must explicitly tell PyInstaller about these files and where they should put them in the bundle.
This is done with PyInstaller's ``--add-data`` flag:

.. code-block:: bash

    pyinstaller myscript.py --add-data "stripes.jpg;."

The first item passed to ``--add-data`` is the "source" file or directory (ex: ``stripes.jpg``) identifying what
PyInstaller should include in the bundle. The item after the semicolon is the "destination" (ex: "``.``"), which
specifies where files should be placed in the bundle, relative to the bundle's root. In the example
above, the ``stripes.jpg`` image is copied to the root of the bundle ("``.``").

One thing to keep in mind. When you are packaging your game in a PyInstaller bundle,
you do not have control over what directory your executable will be run from. Therefore,
it is best to use relative path names in your Python code when loading data files. That
way your game will work no matter where people run the bundled executable from.

Below are some examples that show a few common patterns of how data files can be bundled.
The examples first show a code snippet that demonstrates how data is loaded, followed by the PyInstaller
command to bundle it up.

One Data File
~~~~~~~~~~~~~

If you simply have one data file in the same directory as your script, refer to the data file using a relative path like this:

.. code-block:: python

    sprite = arcade.Sprite("stripes.jpg")

Then, you would use a PyInstaller command like this to include the data file in the bundled executable:

.. code-block:: bash

    pyinstaller myscript.py --add-data "stripes.jpg;."
    ...or...
    pyinstaller myscript.py --add-data "*.jpg;."

One Data Directory
~~~~~~~~~~~~~~~~~~

If you have a directory of data files (such as ``images``), refer to the data directory using a relative path like this:

.. code-block:: python

    sprite = arcade.Sprite("images/player.jpg")
    sprite = arcade.Sprite("images/enemy.jpg")

Then, you would use a PyInstaller command like this to include the directory in the bundled executable:

.. code-block:: bash

    pyinstaller myscript.py --add-data "images;images"

Multiple Data Files and Directories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use the ``--add-data`` flag multiple times to add multiple files and directories into the bundle:

.. code-block:: bash

    pyinstaller myscript.py --add-data "player.jpg;." --add-data "enemy.jpg;." --add-data "music;music"

One Directory for Everything
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Although you can include every data file and directory with separate ``--add-data`` flags, it is suggested
that you write your game so that all of your data files are under one root directory, often named ``resources``. You
can use subdirectories to help organize everything. An example directory tree could look like::

    resources/
    |--- images/
    |    |--- enemy.jpg
    |    |--- player.jpg
    |--- sound/
    |    |--- game_over.wav
    |    |--- laser.wav
    |--- text/
         |--- names.txt

With this approach, it becomes easy to bundle all your data with just a single ``--add-data`` flag. You're code
would use relative pathnames to load resources, something like this:

.. code-block:: python

    sprite = arcade.Sprite("resources/images/player.jpg")
    text = open("resources/text/names.txt").read()

And, you would include this entire directory tree into the bundle like this:

.. code-block:: bash

    pyinstaller myscript.py --add-data "resources;resources"

It is worth spending a bit of time to plan out how you will layout and load your data files in order to keep
the bundling process simple.

Now that you know how to install PyInstaller, include data files, and bundle your game into an executable, you
have what you need to bundle your game and share it with your new fans!

Troubleshooting
---------------

Use a One-Folder Bundle for Troubleshooting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are having problems getting your bundle to work properly, it may help to temporarily
omit the ``--onefile`` flag from the ``pyinstaller`` command.  This will bundle your
game into a one-folder bundle with an executable inside it. This allows you to inspect
the contents of the folder and make sure all of the files are where you expect them
to be. The one-file bundle produced by ``--onefile`` is simply a
self-uncompressing archive of this one-folder bundle.

PyInstaller Not Bundling a Needed Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In most cases, PyInstaller is able to analyze your project and automatically determine
what modules to place in the bundle.  But, if PyInstaller happens to miss a module, you can use
the ``--hidden-import MODULENAME`` flag to explicitly instruct PyInstaller to include a module. See the
`PyInstaller documentation <https://pyinstaller.readthedocs.io/en/stable/usage.html#what-to-bundle-where-to-search>`_
for more details.

Extra Details
-------------

* You will notice that after running ``pyinstaller``, a ``.spec`` file will appear in your directory. This file is generated by PyInstaller and does not need to be saved or checked into your source code repo.
* Executable one-file bundles produced by PyInstaller's ``--onefile`` flag will start up slower than your original application or the one-folder bundle. This is expected because one-file bundles are ultimately just a compressed folder, so they must take time to uncompress themselves each time the bundle is run.
* By default, when PyInstaller creates a bundled application, the application opens a console window. You can suppress the creation of the console window by adding the ``--windowed`` flag to the ``pyinstaller`` command.
* See the PyInstaller documentation below for more details on the topics above, and much more.

PyInstaller Documentation
-------------------------

PyInstaller is a flexible tool that can handle a wide variety of different situations.  For further
reading, here are links to the official PyInstaller documentation:

* PyInstaller home page: http://www.pyinstaller.org/
* PyInstaller Manual: https://pyinstaller.readthedocs.io/en/stable/

.. _Arcade: http://arcade.academy
.. _PyInstaller: http://www.pyinstaller.org
