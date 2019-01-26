.. _how-to-compile:

How to Compile
==============

Windows
^^^^^^^

Prep your system by getting the needed Python packages:

``pip install wheel sphinx coveralls sphinx_rtd_theme pyglet pyglet_ffmpeg numpy pytest pillow``

Create your own fork of the repository, and then clone it on your
computer.

From the base directory, there is a "make" batch file that can be run
with a number of different arguments, some of them listed here:

* ``make full`` - This compiles the source, installs the package on the local
  computer, compiles the documentation, and runs all the unit tests.
* ``make doc`` - This compiles the documentation. Resulting documentation will
  be in ``doc/build/html``.
* ``make fast`` - This compiles and installs the source code. It does not
  create the documentation or run any unit tests.
* ``make test`` - This runs the tests.
* ``make`` - Displays all the arguments "make" supports.

Note: Placing test programs in the root of the project folder will pull from the
source code in the arcade library, rather than the library installed in the
Python interpreter. This is helpful because you can avoid the compile step.
Just make sure not to check in your test code.

Linux
^^^^^

Create your own fork of the repository, and then clone it on your
computer.

Prep your system by downloading the needed packages:

``sudo apt-get install python-dev``

``sudo pip3 install wheel sphinx coveralls sphinx_rtd_theme pyglet pyglet_ffmpeg numpy pytest pillow``

Then, from the terminal you can run any of the following scripts:

* ``sudo ./make.sh`` - Compile, install, make documentation, and run unit tests.
