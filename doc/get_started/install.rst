
.. .. include:: /links.rst

.. _install:

Install
=======

.. _install_requirements:

Requirements
------------

All systems require Python 3.9 or higher on a desktop or laptop device.

.. important:: Yes, this means and mobile are currently unsupported.

               Please see the following to learn more:

               * :ref:`Web browsers <faq_web>`
               * :ref:`Android <faq_android>`, :ref:`iOS <faq_ios>`, and :ref:`iPad <faq_ipad>`


Windows, Linux, and Intel Mac
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Convertibles with Intel or AMD processors under 10 years old will likely work.

Windows
"""""""

To avoid strange issues, install Python as follows:

#. Download Python from the `official Windows download page <https://www.python.org/downloads/windows/>`_
#. While installing, look for a checkbox marked "Add Python to PATH"
#. When you see it, make sure it is checked before proceeding

.. important:: Avoid the Microsoft Store version of Python.

               It has a history of hard-to-fix bugs which will make things
               far more difficult than they need to be.

.. _requirements_mac_mseries:

M-Series Macs
"""""""""""""
Macs with Apple's M-series processors were first introduced in 2020. These mostly work aside from
a few issues related to window focus and unsigned applications. If something odd happens, you
can always :ref:`ask for help. <how-to-get-help>`.

.. _requirements_raspi:

Raspberry Pi
""""""""""""
For Raspberry Pi boards:

* The 4, 400, and 5 series are known to work under Linux
* None of the Zero, Pico, 3, or any earlier models work

The compatible Pi boards all support OpenGL ES 3.1 plus certain extensions. Other brands
of SBCs which support the same features may work, but the Arcade and :py:mod:`pyglet` teams
have not tested any. If your code uses an OpenGL ES feature which is not suported by your board,
your code will fail, but it should not damage your board.

To learn more, please see the `pyglet manual page on OpenGL ES <pyglet-opengles>`_.

.. pending: post-3.0 cleanup # Faster and more reliable than getting the external ref syntax to work
.. _pyglet-opengles: https://pyglet.readthedocs.io/en/development/programming_guide/opengles.html

Using pip
---------

.. Tip::

    For beginners unfamiliar with python a more in depth guide to
    installing Python and Arcade can be found in the :ref:`arcade_book`.

The most common way to install Arcade is to use ``pip``.
This will install the latest version of Arcade from `PyPI`_.

.. code-block:: bash

    pip install arcade

If you are installing Arcade directly into your system python meaning
you are not using a virtual environment (or don't know that that is)
you may need to use the ``--user`` flag to install Arcade just for your user.

.. code-block:: bash

    pip install arcade --user

Upgrading an existing installation of Arcade can be done with the following command

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

This installs Arcade in editable mode so you can make changes to the code and see the changes immediately.
Also consider forking the repository on github installing your fork instead.

Running examples
----------------

Arcade comes with a rich set of examples that demonstrate basic usage of the library.

To test that the installation was successful, check out the :ref:`example-code`
section and run one or more of the examples. The command to run the example is
in the header of each example file.

For example::

    python -m arcade.examples.sprite_explosion_bitmapped


Batteries Included
------------------

:ref:`resources` mean you're ready to start right away. Since all of Arcade's assets are
:ref:`permissive_almost_all_public` or similarly licensed, you're free to create games
however you like.

* :ref:`The Built-In Resources <resources>` page lets you preview Arcade's built-in assets
* :ref:`The Platformer Tutorial <platformer_tutorial>` will help you get started right away
