.. _how-to-compile:

How to Compile
==============

Windows
^^^^^^^

Prep your system by getting needed Python packages:

``pip install wheel sphinx coveralls sphinx_rtd_theme pyglet numpy``

Create your own fork of the repository, and then clone it on your
computer.

From the base directory, there are three batch files that can be run:

* ``make`` - This compiles the source, installs the package on the local
  computer, compiles the documentation, and runs all the unit tests.
* ``makedoc`` - This compiles the documentation. Resulting documentation will
  be in ``doc/build/html``.
* ``makefast`` - This compiles and installs the source code. It does not
  create the documentation or run any unit tests.

Note: Placing test programs in the root of the project folder will pull from the
source code in the arcade library, rather than the library installed in the
Python interpreter. This is helpful because you can avoid the compile step.
Just make sure not to check in your test code.

Linux
^^^^^

Create your own fork of the repository, and then clone it on your
computer.

Prep your system by downloading needed packages:

``sudo apt-get install python-dev``

``sudo pip3 install wheel sphinx coveralls sphinx_rtd_theme pyglet numpy``

Then, from the terminal you can run any of the following scripts:

* ``sudo make.sh`` - Compile, install, make documentation, and run unit tests.
* ``sudo makefast.sh`` - Compile, install.
* ``makedoc.sh`` - Make documentation.
