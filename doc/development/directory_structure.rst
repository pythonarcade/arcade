.. _directory-structure:

Directory Structure
===================

+------------------------+----------------------------------------------------+
| Directory              | Description                                        |
+========================+====================================================+
| \\arcade               | Source code for the arcade library.                |
+------------------------+----------------------------------------------------+
| \\arcade\\color        | Submodule with predefined colors.                  |
+------------------------+----------------------------------------------------+
| \\arcade\\key          | Submodule with keyboard id codes.                  |
+------------------------+----------------------------------------------------+
| \\build                | All built code from the compile script goes        |
|                        | here.                                              |
+------------------------+----------------------------------------------------+
| \\dist                 | Distributable Python wheels go here after the      |
|                        | build script has run.                              |
+------------------------+----------------------------------------------------+
| \\doc                  | Arcade documentation. Note that API documentation  |
|                        | is in docstrings along with the source.            |
+------------------------+----------------------------------------------------+
| \\doc\\source          | Source rst files for the documentation.            |
+------------------------+----------------------------------------------------+
| \\doc\\source\\examples| All the example code                               |
+------------------------+----------------------------------------------------+
| \\doc\\source\\images  | Images used in the documentation.                  |
+------------------------+----------------------------------------------------+
| \\doc\\build\\html     | After making the documentation, all the HTML code  |
|                        | goes here. Look at this in a web browser to see    |
|                        | what the documentation will look like.             |
+------------------------+----------------------------------------------------+
| \\examples             | Example code showing how to use Arcade.            |
+------------------------+----------------------------------------------------+
| \\tests                | Unit tests. Most unit tests are part of the        |
|                        | docstrings.                                        |
+------------------------+----------------------------------------------------+

Also see :ref:`how-to-compile`.
