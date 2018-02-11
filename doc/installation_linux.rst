Installation on Linux
=====================

Ubuntu Instructions
-------------------

The Arcade library is Python 3.x only. Most versions of Linux come with
Python 2.x. You'll need to install Python 3 and use it instead of the
built-in Python 2.x. (Usually on Linux and Mac, you can type ``python3``
instead of ``python`` once installed. Same with ``pip3`` instead of
``pip`` to install packages to Python 3.x)

Install Python 3 and some image dependencies:

.. code-block:: bash

    apt update && sudo apt install -y python3-dev python3-pip libjpeg-dev zlib1g-dev

Check that you have at least Python 3.6 with:

.. code-block:: bash

    python3 -V

If you have version 3.5, you'll need to find instructions on how to install
3.6 or higher on your distribution instead of 3.5. Starting with Ubuntu 17,
3.6 should come by default.

Next, install the "arcade" library along with a "gi" library it requires for sound:

.. code-block:: bash

    sudo pip3 install setuptools
    sudo pip3 install arcade

For sound support, you can install ``gi``. However this library appears
to cause issues with some systems. See:

https://github.com/pvcraven/arcade/issues/177

.. code-block:: bash

    sudo pip3 install gi

