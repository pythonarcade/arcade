Installation on Linux
=====================

Ubuntu Instructions
-------------------

The Arcade library is Python 3.6+ only. Most versions of Linux come with
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

You need at least version 3.6. If you have that,
you should be ready to install Arcade:

.. code-block:: bash

    sudo pip3 install arcade

Raspberry Pi Instructions
-------------------------

Arcade required OpenGL graphics 3.3 or higher. Unfortunately the Raspberry Pi
does not support this, Arcade can not run on the Raspberry Pi.