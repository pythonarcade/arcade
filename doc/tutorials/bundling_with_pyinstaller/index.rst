.. _bundle_into_redistributable:

Bundling a Game with PyInstaller
================================

.. image:: ../../images/floppy-disk.svg
    :width: 30%
    :class: right-image

You've written your game using Arcade and it is a masterpiece! Congrats! Now
you want to share it with others. That usually means helping people install
Python, downloading the necessary modules, copying your code, and then getting
it all working. Sharing is not an easy task. Well, PyInstaller_ can change all
that!

PyInstaller_ is a tool for Python that lets you bundle up an entire Python
application into a one-file executable bundle that you can easily share.
Thankfully, it works great with Arcade!

We will be demonstrating usage with Windows, but everything should work exactly
the same across Windows, Mac, and Linux. Note that you can only build for the
system you are on. This means that in order to make a Windows build, you must
be on a Windows machine, same thing for Linux and Mac. 

Bundling a Simple Arcade Script
-------------------------------

.. image:: ../../images/script.svg
    :width: 20%
    :class: right-image

To demonstrate how PyInstaller works, we will:

* Install PyInstaller
* Create a simple example application that uses Arcade
* Bundle the application into a one-file executable
* Run the application

First, make sure both Arcade and PyInstaller are installed in your Python environment with:

.. code-block:: bash

    pip install arcade pyinstaller

Then we need our game. In this case, we'll start simple. We need a one-file game that doesn't require
any additional images or sounds. Once we have that working, we can get more complicated.
Create a file called ``main.py`` that contains the following:

.. code-block:: python
    :caption: Sample game -- main.py

    import arcade

    window = arcade.open_window(400, 400, "My Game")

    window.clear()
    arcade.draw_circle_filled(200, 200, 100, arcade.color.BLUE)
    arcade.finish_render()

    arcade.run()

Now, create a one-file executable bundle file by running PyInstaller from the command-line:

.. code-block:: bash

    pyinstaller main.py --onefile

PyInstaller generates the executable that is a bundle of your game. It puts it in the ``dist\`` folder under your current working directory. Look for a
file named ``main.exe`` in ``dist\``. Run this and see the example application start up!

You can copy this file wherever you want on your computer and run it. Or, share it with others. Everything your
script needs is inside this executable file.

For simple games, this is all you need to know! But, if your game loads any kind of data files from disk, continue reading.

Handling Data Files
-------------------

.. image:: ../../images/data-files.svg
    :width: 20%
    :class: right-image

When creating a bundle, PyInstaller first examines your project and automatically identifies nearly everything your project needs (a Python interpreter,
installed modules, etc). But, it can't automatically determine what data files your game is loading from disk (images, sounds,
maps). So, you must explicitly tell PyInstaller about these files and where it should put them in the bundle.
This is done with PyInstaller's ``--add-data`` flag:

.. code-block:: bash

    pyinstaller main.py --add-data "stripes.jpg;."

The first item passed to ``--add-data`` is the "source" file or directory (ex: ``stripes.jpg``) identifying what
PyInstaller should include in the bundle. The item after the semicolon is the "destination" (ex: "``.``"), which
specifies where files should be placed in the bundle, relative to the bundle's root. In the example
above, the ``stripes.jpg`` image is copied to the root of the bundle ("``.``").

After instructing PyInstaller to include data files in a bundle, you must make sure your code loads
the data files from the correct directory. When you share your game's bundle, you have no control over what directory
the user will run your bundle from. This is complicated by the fact that a one-file PyInstaller
bundle is uncompressed at runtime to a random temporary directory and then executed from there. This document describes
one simple approach that allows your code to execute and load files when running in a PyInstaller bundle AND also be
able to run when not bundled.

You need to do two things. First, the snippet below must be placed at the beginning of your script:

.. code-block:: python

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)

This snippet uses ``sys.frozen`` and ``sys._MEIPASS``, which are both set by PyInstaller. The ``sys.frozen`` setting
indicates whether code is running from a bundle ("frozen"). If the code is "frozen", the working
directory is changed to the root of where the bundle has been uncompressed to (``sys._MEIPASS``). PyInstaller often
uncompresses its one-file bundles to a directory named something like: ``C:\Users\user\AppData\Local\Temp\_MEI123456``.

Second, once the code above has set the current working directory, all file paths in your code can be relative
paths (ex: ``resources\images\stripes.jpg``) as opposed to absolute paths (ex:
``C:\projects\mygame\resources\images\stripes.jpg``).  If you do these two things and add data files to
your package as demonstrated below, your code will be able to run "normally" as well as running in a bundle.

Below are some examples that show a few common patterns of how data files can be included in a PyInstaller bundle.
The examples first show a code snippet that demonstrates how data is loaded (relative path names), followed by the
PyInstaller command to copy data files into the bundle.  They all assume that the ``os.chdir()`` snippet
of code listed above is being used.

One Data File
~~~~~~~~~~~~~

If you simply have one data file in the same directory as your script, refer to the data file using a relative path like this:

.. code-block:: python

    sprite = arcade.Sprite("stripes.jpg")

Then, you would use a PyInstaller command like this to include the data file in the bundled executable:

.. code-block:: bash

    pyinstaller main.py --add-data "stripes.jpg;."
    ...or...
    pyinstaller main.py --add-data "*.jpg;."

One Data Directory
~~~~~~~~~~~~~~~~~~

.. image:: ../../images/document-icon.svg
    :width: 20%
    :class: right-image

If you have a directory of data files (such as ``images``), refer to the data directory using a relative path like this:

.. code-block:: python

    sprite = arcade.Sprite("images/player.jpg")
    sprite = arcade.Sprite("images/enemy.jpg")

Then, you would use a PyInstaller command like this to include the directory in the bundled executable:

.. code-block:: bash

    pyinstaller main.py --add-data "images;images"

Multiple Data Files and Directories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use the ``--add-data`` flag multiple times to add multiple files and directories into the bundle:

.. code-block:: bash

    pyinstaller main.py --add-data "player.jpg;." --add-data "enemy.jpg;." --add-data "music;music"

One Directory for Everything
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Although you can include every data file and directory with separate ``--add-data`` flags, it is suggested
that you write your game so that all of your data files are under one root directory, often named ``resources``. You
can use subdirectories to help organize everything. An example directory tree could look like::

    project/
    |--- main.py
    |--- resources/
         |--- images/
         |    |--- enemy.jpg
         |    |--- player.jpg
         |--- sound/
         |    |--- game_over.wav
         |    |--- laser.wav
         |--- text/
              |--- names.txt

With this approach, it becomes easy to bundle all your data with just a single ``--add-data`` flag. Your code
would use relative pathnames to load resources, something like this:

.. code-block:: python

    sprite = arcade.Sprite("resources/images/player.jpg")
    text = open("resources/text/names.txt").read()

And, you would include this entire directory tree into the bundle like this:

.. code-block:: bash

    pyinstaller main.py --add-data "resources;resources"

It is worth spending a bit of time to plan out how you will layout and load your data files in order to keep
the bundling process simple.

The technique of handling data files described above is just one approach. If you want more control and flexibility
in handling data files, learn about the different path information that is available by reading the
`PyInstaller Run-Time Information <https://pyinstaller.readthedocs.io/en/stable/runtime-information.html>`_
documentation.

Now that you know how to install PyInstaller, include data files, and bundle your game into an executable, you
have what you need to bundle your game and share it with your new fans!

Troubleshooting
---------------

.. image:: ../../images/detective.svg
    :width: 30%
    :class: right-image

Use a One-Folder Bundle for Troubleshooting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are having problems getting your bundle to work properly, it may help to temporarily
omit the ``--onefile`` flag from the ``pyinstaller`` command.  This will bundle your
game into a one-folder bundle with an executable inside it. This allows you to inspect
the contents of the folder and make sure all of the files are where you expect them
to be. The one-file bundle produced by ``--onefile`` is simply a
self-uncompressing archive of this one-folder bundle.

Specifying Your Own Resource Handles in ``--onefile`` mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See: :ref:`resource_handles_one_file_builds`.

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
* PyInstaller 4.x was used in this tutorial.

PyInstaller Documentation
-------------------------

PyInstaller is a flexible tool that can handle a wide variety of different situations.  For further
reading, here are links to the official PyInstaller documentation and GitHub page:

* PyInstaller Manual: https://pyinstaller.readthedocs.io/en/stable/
* PyInstaller GitHub: https://github.com/pyinstaller/pyinstaller

.. _Arcade: http://arcade.academy
.. _PyInstaller: https://pyinstaller.readthedocs.io/en/stable/
