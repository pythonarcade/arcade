
.. include:: /links.rst

.. _install:

Install
=======

Using pip
---------

.. Tip::

    For beginners unfamiliar with Python, a more in depth guide to
    installing Python and Arcade can be found in the :ref:`arcade_book`.

The most common way to install Arcade is to use the ``pip`` package manager.
This will install the latest version of Arcade from `PyPI`_.

.. code-block:: bash

    pip install arcade

If you are installing Arcade directly into your system Python, meaning
you are not using a virtual environment (or don't know what that is),
you may need to use the ``--user`` flag to install Arcade just for your user.

.. code-block:: bash

    pip install arcade --user

Upgrading an existing installation of Arcade can be done with the following command:

.. code-block:: bash

    pip install -I https://github.com/pythonarcade/arcade/archive/refs/heads/development.zip

The ``-I`` flag is used to force reinstall the package completely ignoring what you have installed.

Development version
-------------------

Pre-releases of Arcade may appear on `PyPI`_ using the `dev` suffix.
It's also quick and easy to install the latest development version from github

If you prefer to install from git::

    git clone https://github.com/pythonarcade/arcade
    cd arcade
    pip install -e .

This installs Arcade in editable mode, so you can make changes to the code and see the changes immediately.
Also consider forking the repository on github installing your fork instead.

Running examples
----------------

Arcade comes with a rich set of examples that demonstrate basic usage of the library.

To test that the installation was successful, check out the :ref:`example-code`
section and run one or more of the examples. The command to run the example is
in the header of each example file.

For example::

    python -m arcade.examples.sprite_explosion_bitmapped

Built-in resource
------------------

Arcade comes with a set of built-in assets that can be used in simple project
while learning the library. See the :ref:`resources` section.
