.. _how-to-compile:

How to Compile
==============

Windows
^^^^^^^

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

There aren't UNIX build scripts yet, but by looking at the batch files you
could likely come up with some shell files that would work.
