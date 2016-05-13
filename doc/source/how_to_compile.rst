How to Compile
==============

Directory Structure
^^^^^^^^^^^^^^^^^^^

The directory structure layout::

  \arcade - source code for the arcade library
  \arcade\color - submodule with colors
  \arcade\key - submodule with keyboard ids
  \build - all built code from the compile script goes here
  \dist - distributable wheels are put here by the compile script
  \doc - documentation
  \doc\build - built documentation goes here
  \doc\build\html - this is where the resulting html docs go
  \doc\source - source restructured text files for the docs go here
  \doc\source\_static - required directory for rst
  \doc\source\examples - collection of code examples goes here
  \doc\source\images - images for documentation
  \doc\source\internal - required directory for rst
  \experimental - unused items
  \tests - unit tests (most tests are in the arcade docstrings)


Windows
^^^^^^^

From the base directory, there are three batch files that can be run:

* ``make`` - This compiles the source, installs the package on the local
  computer, compiles the documentation, and runs all the unit tests.
* ``makedoc`` - This compiles the documentation.
* ``makefast`` - This compiles and installs the source code. It does not
  create the documentation or run any unit tests.