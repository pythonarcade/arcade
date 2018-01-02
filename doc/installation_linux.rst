Installation on Linux
=====================

Ubuntu 16.04 Instructions
-------------------------

First, install Python 3 and some image dependencies:

.. code-block:: bash

    apt update && sudo apt install -y python3-dev python3-pip libjpeg-dev zlib1g-dev

Next, install the "arcade" library along with a "gi" library it requires for sound:

    sudo pip3 install gi arcade

