Linux
=====

The Arcade library is Python 3.7+ only. First check your version of Python to ensure
you have 3.7 or higher:

.. code-block:: bash

    python -V

If your version shows Python 2.X then try running with:

.. code-block:: bash

    python3 -V

If that works and shows you Python 3.7+, then anytime you see the ``python`` command, replace it with ``python3``.

If you do not have Python 3.7+, please lookup how to install it for your specific distro of Linux.
For Ubuntu/Debian this would be with the below command, if you did have Python 3.7, you can skip this step:

.. code-block:: bash

    sudo apt install python3 python3-pip libjpeg-dev zlib1g-dev

Next you'll need to setup a Virtual Environment. Arcade should always be installed with a virtual environment.
Installing outside of a virtual environment can lead to unintended consequences and bugs with your system.
You can read more about Virtual Environments at this page: https://docs.python.org/3/tutorial/venv.html

.. code-block:: bash

    python -m venv my_venv

This creates a new folder called ``my_venv`` which contains your Python virtual environment.
You can now activate it with:

.. code-block:: bash

    source my_venv/bin/activate

And deactivate it with:

.. code-block:: bash

    deactivate

Once your venv is activated, you can install Arcade with:

.. code-block:: bash

    pip install arcade

Raspberry Pi Instructions
-------------------------

Arcade required OpenGL graphics 3.3 or higher. Unfortunately the Raspberry Pi
does not support this, Arcade can not run on the Raspberry Pi.
