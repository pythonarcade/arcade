
.. _platformer_part_one:

Step 1 - Install and Open a Window
----------------------------------

Our first step is to make sure everything is installed, and that we can at least
get a window open.

Installation
~~~~~~~~~~~~
* Make sure Python is installed. `Download Python here <https://www.python.org/downloads/>`_
  if you don't already have it.
* `Download this bundle with code, images, and sounds <../../_static/platform_tutorial.zip>`_.
  (Images are from `kenney.nl`_.)
  Your file structure should look like:

.. image:: file_structure.png
    :scale: 75%

* Make sure the `Arcade library <https://pypi.org/project/arcade/>`_ is installed.

  * Install Arcade with ``pip install arcade`` on Windows
    or ``pip3 install arcade`` on Mac/Linux. Or install by using a venv.
  * Here are the longer, official :ref:`installation-instructions`.

I highly recommend using the free community edition of PyCharm as an editor.
If you do, see :ref:`install-pycharm`.

.. _kenney.nl: https://kenney.nl/


Open a Window
~~~~~~~~~~~~~

The example below opens up a blank window. Set up a project and get the code
below working. (It is also in the zip file as
``01_open_window.py``.)

.. note::

  This is a fixed-size window. It is possible to have  a
  :ref:`resizable_window` or a :ref:`full_screen_example`, but there are more
  interesting things we can do first. Therefore we'll stick with a fixed-size
  window for this tutorial.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/01_open_window.py
    :caption: 01_open_window.py - Open a Window
    :linenos:

Once you get the code working, figure out how to:

* Change the screen size
* Change the title
* Change the background color

  * See the documentation for :ref:`color`
  * See the documentation for :ref:`csscolor`

* Look through the documentation for the
  `Window <../../arcade.html#arcade.Window>`_ class to get an idea of everything
  it can do.

Source Code
~~~~~~~~~~~

* :ref:`01_open_window`