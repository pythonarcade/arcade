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

    apt update && sudo apt install -y python3-dev python3-pip libjpeg-dev zlib1g-dev python-gst-1.0

Check that you have at least Python 3.6 with:

.. code-block:: bash

    python3 -V

If you have version 3.5, you'll need to find instructions on how to install
3.6 or higher on your distribution instead of 3.5. Starting with Ubuntu 17,
3.6 should come by default. Linux Mint still uses 3.5.
`Python 3.6.4 Installation Instructions for Mint <https://tecadmin.net/install-python-3-6-ubuntu-linuxmint/>`_.

If you everything worked, you should be ready to install Arcade:

.. code-block:: bash

    sudo pip3 install arcade

Note: For sound support Arcade uses the gstreamer package. This installs only
via ``apt-get`` and doesn't support virtual environments well at all.

Raspberry Pi Instructions
-------------------------

*(Contributed by Patrick)*

The Arcade library is Python 3.6+ only. Currently (July 2018) Rasbian come with
Python 3.5.x You'll need to install Python 3.6+ and use it instead of the
built-in Python 3.5.x.

To install Python 3.6+ first do:

.. code-block:: bash

    sudo apt-get update
    sudo apt-get install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev
    sudo apt-get install libffi-dev
    cd Downloads
    wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tar.xz
    tar xf Python-3.7.0.tar.xz
    cd Python-3.7.0
    ./configure
    make
    sudo make altinstall

Now that Python3.7 (or whatever the latest version is) is installed, you must use it and not the default python3 from now on.

Now install Arcade and the files it needs:

.. code-block:: bash

    sudo apt install -y python3-dev python3-pip libjpeg-dev zlib1g-dev python-gst-1.0

If you everything worked, you should be ready to install Arcade:

.. code-block:: bash

    sudo pip3.7 install arcade

Note: For sound support Arcade uses the gstreamer package. This is already installed with Rasbian.