.. _distribute_macos:

Building for MacOS
==================

This page documents the process of building an Arcade game for MacOS using `Briefcase <https://briefcase.readthedocs.io/en/latest/>`_.

Installation
------------

To begin, install and use `Briefcase <https://briefcase.readthedocs.io/en/latest/>`_ by executing:

* ``pip install briefcase``
* ``mkdir ~/path/to/game/dist``
* ``cd ~/path/to/game/dist``
* ``cookiecutter https://github.com/pybee/briefcase-template``

    Choose the values that suit you. Most defaults work, except for **Select gui_framework**, for which you *must* choose ``2 - None``.

    You should automatically be in your new ``dist/`` directory.

    Moving forward, replace ``appname`` with the first value you supplied to Cookiecutter (the name of your game).

* Open ``appname/setup.py``, find ``install_requires``, and add ``arcade`` and any of your additional requirements, like so:

.. literalinclude:: ../../arcade/doc/examples/install_requires.py
    :linenos:

* Open ``appname/__main__.py`` and edit the file to look like this:

.. literalinclude:: ../../arcade/doc/examples/briefcase__main__.py
    :linenos:

* Open ``appname/app.py`` and edit the file to look like this:

.. literalinclude:: ../../arcade/doc/examples/briefcase_app.py
    :linenos:
