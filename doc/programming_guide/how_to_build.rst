.. _how-to-compile:

How to Build
============

Windows
^^^^^^^

Prep your system by getting the needed Python packages, listed in the
``requirements.txt`` file.

Create your own fork of the repository, and then clone it on your
computer.

From the base directory, there is a "make" batch file that can be run
with a number of different arguments, some of them listed here:

* ``make test`` - This runs the tests.
* ``make testcov`` - This runs the tests, and lists coverage
* ``make dist`` - Makes the distributable wheels
* ``make deploy_pypi`` - Uploads wheels to PyPi

Note: Placing test programs in the root of the project folder will pull from the
source code in the arcade library, rather than the library installed in the
Python interpreter. This is helpful because you can avoid the compile step.
Just make sure not to check in your test code.

To build the docs, switch to the ``doc`` directory, and type ``make html``.

Linux
^^^^^

Create your own fork of the repository, and then clone it on your
computer.

Prep your system by downloading the needed packages:

``sudo apt-get install python-dev``
