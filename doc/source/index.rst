.. Arcade documentation master file, created by
   sphinx-quickstart on Mon Dec 28 23:02:22 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The Arcade Python Package
=========================

|build-status-travis| |build-status-appveyor| |coverage|

Arcade is an easy-to-learn Python library for creating 2d video games. The API is designed to allow progressive functionality as you learn to code. To make images, you do not need to learn to define functions. To make animations, you don't need to understand classes. But once you do understand classes, it is easy to put together classic video games.

The source is available on GitHub: https://github.com/pvcraven/arcade

The list of current issues is on GitHub: https://github.com/pvcraven/arcade/issues

Documentation
-------------

.. toctree::
   :maxdepth: 4

   examples/index
   installation
   arcade
   quick_index

.. automodule:: arcade

.. include:: ../../license.rst

.. |build-status-travis| image:: https://travis-ci.org/pvcraven/arcade.svg
    :target: https://travis-ci.org/pvcraven/arcade
    :alt: build status
    :scale: 100%

.. |build-status-appveyor| image:: https://ci.appveyor.com/api/projects/status/github/pvcraven/arcade
    :target: https://ci.appveyor.com/project/pvcraven/arcade-ekjdf
    :alt: build status
    :scale: 100%

.. |coverage| image:: https://coveralls.io/repos/pvcraven/arcade/badge.svg?branch=master&service=github
    :alt: Test Coverage Status
    :scale: 100%
    :target: https://coveralls.io/github/pvcraven/arcade?branch=master
