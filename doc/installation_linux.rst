Installation on Linux
=====================

.. code-block:: bash

    apt update && sudo apt install -y python3-dev python3-pip git libavbin-dev libavbin0 libjpeg-dev zlib1g-dev
    sudo pip3 install virtualenv virtualenvwrapper
    virtualenv ~/.virtualenvs/arcade -p python3
    source ~/.virtualenvs/arcade/bin/activate
    pip install arcade

Issues with avbin?
------------------

The libavbin items help with sound.
There is an issue getting this library on newer versions of Ubuntu.


.. code-block:: bash

    sudo apt-get install -y libasound2
