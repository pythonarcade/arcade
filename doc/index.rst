The Python Arcade Library
=========================

.. raw:: html

    <table style="width:100%;">
      <tr>
        <td>
          <img style="width:50px;" src="_static/character.png"><br/>
          <h2><a href="examples/index.html">Example Code</a></h2>
          <ul>
          <li><a href="examples/drawing_primitives.html">Drawing Primitives</a></li>
          <li><a href="examples/sprite_collect_coins.html">Collect Coins</a></li>
          <li><a href="examples/asteroid_smasher.html">Asteroid Smasher</a></li>
          </ul>
        </td>
        <td>
          <img style="width:78px;" src="_static/download.svg"><br/>
          <h2><a href="installation.html">Installation</a></h2>
          <ul>
          <li><a href="installation_windows.html">Windows</a></li>
          <li><a href="installation_mac.html">Mac</a></li>
          <li><a href="installation_linux.html">Linux</a></li>
          </ul>
        </td>
      </tr>
      <tr>
        <td>
          <img style="width:78px;" src="_static/ereader.svg"><br/>
          <h2><a href="quick_index.html">Quick API Index</a></h2>
          <ul>
          <li><a href="quick_index.html#drawing-module">Drawing Functions</a></li>
          <li><a href="quick_index.html#application-module">Window Class</a></li>
          <li><a href="quick_index.html#sprite-module">Sprites</a></li>
          <li><a href="arcade.html">Full Arcade API Docs</a></li>
          <li><a href="http://arcade-book.readthedocs.io/en/latest/">Learn to Program with Arcade</a> (book)</li>
          </ul>
        </td>
        <td>
          <img style="width:78px;" src="_static/weixin-logo.svg"><br/>
          <h2>More Info</h2>
          <ul>
            <li><a href="diversity.html">Diversity</a></li>
            <li><a href="pygame_comparison.html">Pygame Comparison</a></li>
            <li><a href="performance_tips.html">Performance Tips</a></li>
            <li><a href="https://youtu.be/DAWHMHMPVHU">PyCon 2018 Talk</a></li>
            <li><a href="https://www.reddit.com/r/pythonarcade/">Reddit /r/pythonarcade</a></li>
          </ul>
        </td>
      </tr>
      <tr>
        <td>
          <img style="width:78px;" src="_static/sample_games.svg"><br/>
          <h2><a href="sample_games.html">Example Games</a></h2>
          <ul>
            <li><a href="instructions_gameshell.html">GameShell (Hand-held like a GameBoy)</a></li>
            <li><a href="examples/pyinstaller.html">Distributing games with PyInstaller</a></li>
          </ul>
        </td>
        <td>
          <img style="width:78px;" src="_static/code.svg"><br/>
          <h2>Source Code</h2>
          <ul>
            <li><a href="https://github.com/pvcraven/arcade">GitHub</a></li>
            <li><a href="release_notes.html">Release Notes</a></li>
          </ul>
        </td>
      </tr>
    </table>
    <p></p>
.. raw:: html

    <iframe src="https://player.vimeo.com/video/167449640?byline=0&portrait=0" width="640" height="480" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>
    <p><a href="https://vimeo.com/167449640">The Python Arcade Library Overview</a></p>

Arcade is an easy-to-learn Python library for creating 2D video games. It is
ideal for people learning to program, or developers that want to code a 2D
game without learning a complex framework.

Learn about it:
^^^^^^^^^^^^^^^

* :ref:`installation-instructions`
* :ref:`example-code`
* :ref:`arcade-api`
* :ref:`quick-index`
* `Arcade on PyPi`_
* :ref:`pygame-comparison`

Give feedback:
^^^^^^^^^^^^^^

* `GitHub Arcade Issue List`_
* `Reddit Discussion Group`_
* Email: paul.craven@simpson.edu

Contribute to the development:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* :ref:`how-to-contribute`
* `GitHub Source Code for Arcade`_

The status of the build is here: |build-status-travis| |build-status-appveyor| |coverage|

Examples
--------

.. toctree::
   :maxdepth: 4

   examples/index
   sample_games

Installation
------------

.. toctree::
   :maxdepth: 4

   installation

API Documentation
-----------------

.. toctree::
   :maxdepth: 4

   arcade
   quick_index
   performance_tips

Distribution
------------

.. toctree::
   :maxdepth: 4

   distribute_macos
   instructions_gameshell


How to Contribute
-----------------

.. toctree::
   :maxdepth: 1

   how_to_contribute
   directory_structure
   how_to_compile
   how_to_submit_changes
   diversity

More Information
----------------

.. toctree::
   :maxdepth: 1

   pygame_comparison.rst
   suggested_curriculum.rst

.. automodule:: arcade

.. include:: ../license.rst

.. |build-status-travis| image:: https://travis-ci.org/pvcraven/arcade.svg
    :target: https://travis-ci.org/pvcraven/arcade
    :alt: build status

.. |build-status-appveyor| image:: https://ci.appveyor.com/api/projects/status/github/pvcraven/arcade
    :target: https://ci.appveyor.com/project/pvcraven/arcade-ekjdf
    :alt: build status

.. |coverage| image:: https://coveralls.io/repos/pvcraven/arcade/badge.svg?branch=master&service=github
    :alt: Test Coverage Status
    :target: https://coveralls.io/github/pvcraven/arcade?branch=master

.. _GitHub Source Code for Arcade: https://github.com/pvcraven/arcade
.. _GitHub Arcade Issue List: https://github.com/pvcraven/arcade/issues
.. _Arcade on PyPi: https://pypi.python.org/pypi/arcade
.. _Reddit Discussion Group: https://www.reddit.com/r/pythonarcade/
