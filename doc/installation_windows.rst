Installation on Windows
=======================

To develop with the Arcade library, we need to install Python, then install
Arcade.

Step 1: Install Python
----------------------

Install Python from the official Python website:

https://www.python.org/downloads/

The website gives you the option of downloading two different versions:
Version 3.x.x or version 2.x.x. The Arcade library requires Python
beginning with 3.x.x.

When installing Python, make sure to add Pthon to the path (1) before clicking the Install button (2).

.. image:: images/setup_windows_1.png
    :width: 450px

After that, you can just close the dialog. There's no need to increase the path length, although it
doesn't hurt anything if you do.

.. image:: images/setup_windows_2.png
    :width: 450px


Step 2: Install The Arcade Library
----------------------------------

If you install Arcade as a pre-built library, there are two options on
how to do it. The best way is to use a "virtual environment." This is
a collection of Python libraries that only apply to your particular project.
You don't have to worry about libraries for other projects conflicting
with your project. You also don't need "administrator" level privileges to
install libraries.

The second-best way is to install the library for the entire system. All
Python instances will have access to the library. You don't have to setup
a virtual environment, and you don't need to import the library for each project.

Install Arcade with PyCharm and a Virtual Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are using PyCharm, setting up a virtual environment is easy. Once you've
got your project, open up the settings:

.. image:: images/venv_setup_1.png
    :width: 300px

Select project interpreter:

.. image:: images/venv_setup_2.png
    :width: 650px

Create a new virtual environment. Make sure the venv is inside your
project folder.

.. image:: images/venv_setup_3.png
    :width: 650px

Now you can install libraries. PyCharm will automatically ask to add them
if you have a file called `requirements.txt` that lists the required libraries.

.. image:: images/venv_setup_4.png
    :width: 650px

Install Arcade System-Wide
^^^^^^^^^^^^^^^^^^^^^^^^^^

Click the Window button in the lower left of your screen (or hit the window
button on your keyboard) and start typing ``command prompt``.

Don't just run the Command Prompt, but instead right-click on it and run as
administrator.

.. image:: images/setup_windows_4.png
    :width: 350px

Next, type ``pip install arcade`` at the command prompt:

.. image:: images/pip_install_arcade_windows.png
    :width: 450px

The video below steps through the process:

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/6ZU8kNoATRo" frameborder="0" allowfullscreen></iframe><p>

Install Arcade The Hard Way
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you successfully installed Arcade the easy way, skip this section. If
you'd rather download the Arcade library directly off PyPi you can at:

https://pypi.python.org/pypi/arcade

Or you can get the source code for the library from GitHub:

https://github.com/pvcraven/arcade

