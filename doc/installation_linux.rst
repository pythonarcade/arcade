Installation on Linux
=====================

Ubuntu 16.04 Instructions
-----------------

We will use a virtual python environment to install arcade.

.. code-block:: bash

    apt update && sudo apt install -y python3-dev python3-pip libjpeg-dev zlib1g-dev
    sudo pip3 install virtualenv virtualenvwrapper
    virtualenv ~/.virtualenvs/arcade -p python3
    source ~/.virtualenvs/arcade/bin/activate
    pip install arcade

In order for sound to work we need to install avbin from here:
https://github.com/AVbin/AVbin/downloads

Download the AVbin 11-alpha4 version.
Be sure to download the correct architecture.

.. code-block:: bash

    cd Download/Location
    chmod +x install-avbin-linux-x86-64-v11alpha4 #You may have a different architecture
    sudo ./install-avbin-linux-x86-64-v11alpha4

Issues with avbin?
------------------

The libavbin items help with sound.
There is an issue getting this library on newer versions of Ubuntu.


.. code-block:: bash

    sudo apt-get install -y libasound2
