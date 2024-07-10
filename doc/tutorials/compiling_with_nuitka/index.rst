.. _compile_with_nuitka:

Compiling a Game with Nuitka
============================

.. image:: ../../images/floppy-disk.svg
    :width: 30%
    :class: right-image

So you have successfully written your dream game with Arcade and now, you want
to share it with your friends and family. Good idea! But there is a *small* issue.
Sadly, they are not a tech geek as big as you are and don't have any knowledge
about Python and its working :(. Though :ref:`bundle_into_redistributable` *is* a good option, the 
executables it produces can sometime take up a good amount of space and antiviruses
raise false positives almost every time. But Nuitka_ is here to solve all your
problems!

Nuitka_ is a tool which compiles your Python code to machine code directly, and 
bundles your application's source code in dll files. This way, you get two benefits:

* The source code is safe in dll files.
* The application gets a performance boosts in many cases.
* The resulting executable's size is small.

We are using Windows for this tutorial, but most of the commands can be used as-it-is
on other platforms including Linux and Mac.

.. warning::
    Builds are platform dependent!

    For example, a Windows build will not work out-of-the-box on a
    different OS. The same goes for Linux and Mac builds on other
    platforms.

    You can use a Mac or a Linux system to compile your game for those
    platforms. 

    To compile for a different platform than your current one, you may
    be able to use a Virtual Machine or WINE/Proton. However, these
    options are not officially supported and are not covered in this
    tutorial.

Compiling a Simple Arcade Script
--------------------------------

For this tutorial, we will use the code from :ref:`platformer_tutorial`. 

* First, we have to install Nuitka_ with the following command:

.. code-block:: bash

    pip install nuitka

We will be using the code from `this file <https://github.com/pythonarcade/arcade/blob/development/arcade/examples/platform_tutorial/17_views.py>`_.

Converting that code to a standalone executable is as easy as:

.. code-block:: bash

    python -m nuitka 17_views.py --standalone --enable-plugin=numpy

Now sit back and relax. Might as well go and grab a cup of coffee since compilation
takes time, sometimes maybe up to 2 hours, depending on your machine's specs.
After the process is finished, two new folders named ``17_views.py.dist`` and
``17_views.py.build`` will popup. You can safely ignore the build folder for now.
Just go to the dis folder and run ``17_views.exe`` file , present in there. If there are no
errors, then the application should work perfectly. 

Congratulations! You have successfully compiled your Python code to a standalone executable!

Note: If you want to compile the code to a single file instead of a folder, just remove the ``standalone``
flag and add the ``onefile`` flag!


But What About Data Files And Folders?
--------------------------------------

Sometimes, our application also uses custom data files which may include sound effects, fonts
etc... In order to bundle them with the application, just use the ``include-data-file`` or
``include-data-dir`` flag:

.. code-block:: bash

    python -m nuitka 17_views.py --standalone --enable-plugin=numpy --include-data-file=C:/Users/Hunter/Desktop/my_game/my_image.png=.

This will copy the file named ``my_image.png`` at the specified location to the root of the executable.

To bundle a whole folder:

.. code-block:: bash

    python -m nuitka 17_views.py --standalone --enable-plugin=numpy --include-data-dir=C:/Users/Hunter/Desktop/my_game/assets=.

This will copy the whole folder named ``assets`` at the specified location to the root of the executable.

.. Note::

    If you want to use a custom resource handles and Nuitka's one-file build see: :ref:`resource_handles_one_file_builds`.

Removing The Console Window
---------------------------

You might have noticed that while opening the executable, a console window automatically
opens. Even though it is helpful in debugging and errors, it does look ugly. You might
think, is there a way to force the console output to a logs file? Well, thanks to Nuitka,
this is also possible:

.. code-block:: bash

    python -m nuitka 17_views.py --standalone --windows-force-stderr-spec=%PROGRAM%logs.txt --windows-force-stdout-spec=%PROGRAM%output.txt

This will automatically create two files, viz ``logs.txt`` and ``output.txt`` in the executable directory which will
contain the stderr and stdout output respectively!


What About A Custom Taskbar Icon?
---------------------------------

Nuitka provides us with the ``windows-icon-from-ico`` and ``windows-icon-from-exe`` flags (**varies for each OS**)
to set custom icons.
The first flag takes a ``.png`` or a ``.ico`` file and sets it as the app icon:

.. code-block:: bash

    python -m nuitka 17_views.py --standalone --windows-icon-from-ico=icon.png

This will set the app icon to icon.png

.. code-block:: bash

    python -m nuitka 17_views.py --standalone --windows-icon-from-exe=C:\Users\Hunter\AppData\Local\Programs\Python\Python310/python.exe

This will set the app icon to Python's icon 😉

Additional Information
----------------------

* This tutorial was tested with Nutika 0.7.x. Later releases are likely to work.

.. _Nuitka: https://nuitka.net/
