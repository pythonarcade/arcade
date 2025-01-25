
.. .. include:: /links.rst

.. _install:

Install
=======

.. _install_requirements:

Requirements
------------
:mod:`pyglet`

All systems require Python 3.9 or higher on a desktop or laptop device.

:ref:`Web <faq_web>` and :ref:`mobile <faq_mobile>` are currently
unsupported.

Windows, Linux, and Intel Mac
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Your computer can likely run Arcade if it supports Python 3.9 or higher.

In general, even older convertible Windows tablets will work as long as they:

#. have an Intel or AMD processor
#. were made in the last 10 years

.. note:: ARM-based Windows or Linux tablets may have issues.

          These devices may or may not work.  the :ref:`requirements_raspi`

Windows
"""""""

To avoid strange issues, install Python as follows:

#. Download Python from the `official Windows download page <https://www.python.org/downloads/windows/>`_
#. While installing, look for a checkbox marked "Add Python to PATH"
#. When you see it, make sure it is checked before proceeding

.. important:: Avoid the Microsoft Store version of Python.

               It has a history of hard-to-fix bugs which make
               development more difficult than it needs to be.

.. _requirements_mac_mseries:

M-Series Macs
"""""""""""""
Apple first released Macs with M-series processors in 2020. They may have a few
issues with window focus and unsigned applications. If something odd happens, you
can always :ref:`ask for help. <how-to-get-help>`.

.. _requirements_raspi:

Raspberry Pi and Other ARM SBCs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Arcade and :py:mod:`pyglet` teams have verified the Raspberry Pi 4 and 5
as working. The Raspberry Pi 400 will also likely work, but other Pi models will not.

To learn more, please see:

* :ref:`faq-raspi`
* :ref:`sbc_supported_raspi`


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


Batteries Included
------------------

:ref:`resources` mean you're ready to start right away. Since all of Arcade's assets are
:ref:`permissive_almost_all_public` or similarly licensed, you're free to create games
however you like.

* :ref:`The Built-In Resources <resources>` page lets you preview Arcade's built-in assets
* :ref:`The Platformer Tutorial <platformer_tutorial>` will help you get started right away
