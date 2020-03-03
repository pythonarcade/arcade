Installation on Windows
=======================

To develop with the Arcade library, we need to install Python, then install
Arcade, and finally install a development environment.

Step 1: Install Python
----------------------

Install Python from the official Python website:

https://www.python.org/downloads/

When installing Python, make sure to customize the installation and add
Python to the path:

.. image:: images/setup_windows_1.png
    :width: 400px

The defaults on the next screen are fine:

.. image:: images/setup_windows_2.png
    :width: 400px

Then install Python for all users:

.. image:: images/setup_windows_3.png
    :width: 400px

A video of the installation is below:

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/KbA6zbUXXP4" frameborder="0" allowfullscreen></iframe><p>


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
    :width: 350px

Select project interpreter:

.. image:: images/venv_setup_2.png
    :width: 350px

Create a new virtual environment. Make sure the venv is inside your
project folder.

.. image:: images/venv_setup_3.png
    :width: 350px

Now you can install libraries. PyCharm will automatically ask to add them
if you have a file called `requirements.txt` that lists the required libraries.

.. image:: images/venv_setup_4.png
    :width: 350px

.. _PyCharm: https://www.jetbrains.com/pycharm/
.. _Sublime: https://www.sublimetext.com/
.. _Wing: https://wingware.com/
.. _Wing 101: http://wingware.com/downloads/wingide-101
.. _Anaconda: http://damnwidget.github.io/anaconda/
