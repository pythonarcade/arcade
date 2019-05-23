:orphan:

.. _release_notes:

Release Notes
=============

Version 2.0.9
-------------

* Fix: Unable to specify path to .tsx file for tiled spritesheet `Issue 360 <https://github.com/pvcraven/arcade/issues/360>`_
* Fix: TypeError: __init__() takes from 3 to 11 positional arguments but 12 were given in text.py `Issue 373 <https://github.com/pvcraven/arcade/issues/373>`_
* Fix: Test create_line_strip `Issue 379 <https://github.com/pvcraven/arcade/issues/379>`_
* Fix: TypeError: draw_rectangle_filled() got an unexpected keyword argument 'border_width' `Issue 385 <https://github.com/pvcraven/arcade/issues/385>`_
* Fix: See about creating a localization/internationalization example `Issue 391 <https://github.com/pvcraven/arcade/issues/391>`_
* Fix: Glitch when you die in the lava in 09_endgame.py `Issue 392 <https://github.com/pvcraven/arcade/issues/392>`_
* Fix: No default font found on ArchLinux and no error message (includes patch)  `Issue 402 <https://github.com/pvcraven/arcade/issues/402>`_
* Fix: Update docs around batch drawing and array_backed_grid.py example  `Issue 403 <https://github.com/pvcraven/arcade/issues/403>`_

Version 2.0.8
-------------

* Add example code from lixingque
* Fix: Drawing primitives example broke in prior release `Issue 365 <https://github.com/pvcraven/arcade/issues/365>`_
* Update: Improve automated testing of all code examples `Issue 326 <https://github.com/pvcraven/arcade/issues/326>`_
* Update: raspberry pi instructions, although it still doesn't work yet
* Fix: Some buffered draw commands not working `Issue 368 <https://github.com/pvcraven/arcade/issues/368>`_
* Remove yml files for build environments that don't work because of OpenGL
* Update requirement.txt files
* Fix mountain examples
* Better error handling when playing sounds
* Remove a few unused example code files


Version 2.0.7
-------------

* Last release improperly required pyglet-ffmpeg, updated to pyglet-ffmpeg2
* Fix: The alpha value seems NOT work with draw_texture_rectangle `Issue 364 <https://github.com/pvcraven/arcade/issues/364>`_
* Fix: draw_xywh_rectangle_textured error `Issue 363 <https://github.com/pvcraven/arcade/issues/363>`_

Version 2.0.6
-------------

* Improve ffmpeg support. Think it works on MacOS and Windows now. `Issue 350 <https://github.com/pvcraven/arcade/issues/350>`_
* Improve buffered drawing command support
* Improve PEP-8 compliance
* Fix for tiled map reader, `Issue 360 <https://github.com/pvcraven/arcade/issues/360>`_
* Fix for animated sprites `Issue 359 <https://github.com/pvcraven/arcade/issues/359>`_
* Remove unused avbin library for mac

Version 2.0.5
-------------

* Issue if scale is set for a sprite that doesn't yet have a texture set. `Issue 354 <https://github.com/pvcraven/arcade/issues/354>`_
* Fix for ``Sprite.set_position`` not working. `Issue 356 <https://github.com/pvcraven/arcade/issues/354>`_

Version 2.0.4
-------------

* Fix for drawing with a border width of 1 `Issue 352 <https://github.com/pvcraven/arcade/issues/352>`_

Version 2.0.3
-------------

Version 2.0.2 was compiled off the wrong branch, so it had a bunch of untested
code. 2.0.3 is what 2.0.2 was supposed to be.

Version 2.0.2
-------------

* Fix for loading a wav file `Issue 344 <https://github.com/pvcraven/arcade/issues/344>`_
* Fix Linux only getting 30 fps `Issue 342 <https://github.com/pvcraven/arcade/issues/342>`_
* Fix error on window creation `Issue 340 <https://github.com/pvcraven/arcade/issues/340>`_
* Fix for graphics cards not supporting multi-sample `Issue 339 <https://github.com/pvcraven/arcade/issues/339>`_
* Fix for set view error on mac `Issue 336 <https://github.com/pvcraven/arcade/issues/336>`_
* Changing scale attribute on Sprite now dynamically changes sprite scale `Issue 331 <https://github.com/pvcraven/arcade/issues/331>`_

Version 2.0.1
-------------

* Turn on multi-sampling so lines could be anti-aliased
  `Issue 325 <https://github.com/pvcraven/arcade/issues/325>`_

Version 2.0.0
-------------

Released 2019-03-10

Lots of improvements in 2.0.0. Too many to list, but the two main improvements:

* Using shaders for sprites, making drawing sprites incredibly fast.
* Using ffmpeg for sound.

Version 1.3.7
-------------

Released 2018-10-28

* Fix for `Issue 275 <https://github.com/pvcraven/arcade/issues/275>`_ where sprites can get blurry.


Version 1.3.6
-------------

Released 2018-10-10

* Bux fix for spatial hashing
* Implement commands for getting a pixel, and image from screen

Version 1.3.5
-------------

Released 08-23-2018

Bug fixes for spatial hashing and sound.

Version 1.3.4
-------------

Released 28-May-2018

New Features
~~~~~~~~~~~~

* `Issue 197 <https://github.com/pvcraven/arcade/issues/197>`_: Add new set of color names that match CSS color names
* `Issue 203 <https://github.com/pvcraven/arcade/issues/203>`_: Add on_update as alternative to update
* Add ability to read .tmx files.

Bug Fixes
~~~~~~~~~

* `Issue 159 <https://github.com/pvcraven/arcade/issues/159>`_: Fix array backed grid buffer example
* `Issue 177 <https://github.com/pvcraven/arcade/issues/177>`_: Kind of fix issue with gi sound library
* `Issue 180 <https://github.com/pvcraven/arcade/issues/180>`_: Fix up API docs with sound
* `Issue 198 <https://github.com/pvcraven/arcade/issues/198>`_: Add start of isometric tile support
* `Issue 210 <https://github.com/pvcraven/arcade/issues/210>`_: Fix bug in MacOS sound handling
* `Issue 213 <https://github.com/pvcraven/arcade/issues/213>`_: Update code with gi streamer
* `Issue 214 <https://github.com/pvcraven/arcade/issues/214>`_: Fix issue with missing images in animated sprites
* `Issue 216 <https://github.com/pvcraven/arcade/issues/216>`_: Fix bug with venv
* `Issue 222 <https://github.com/pvcraven/arcade/issues/222>`_: Fix get_window when using a Window class

Documentation
~~~~~~~~~~~~~

* `Issue 217 <https://github.com/pvcraven/arcade/issues/217>`_: Fix typo in doc string
* `Issue 198 <https://github.com/pvcraven/arcade/issues/198>`_: Add example showing start of isometric tile support


Version 1.3.3
-------------

Released 2018-May-05

New Features
~~~~~~~~~~~~

* `Issue 184 <https://github.com/pvcraven/arcade/issues/184>`_: For sound, wav, mp3, and ogg should work on Linux and Windows. wav and mp3 should work on Mac.

Updated Examples
~~~~~~~~~~~~~~~~

* Add happy face drawing example

Version 1.3.2
-------------

Released 2018-Apr-20

New Features
~~~~~~~~~~~~

* `Issue 189 <https://github.com/pvcraven/arcade/issues/189>`_: Add spatial hashing for faster collision detection
* `Issue 191 <https://github.com/pvcraven/arcade/issues/191>`_: Add function to get the distance between two sprites
* `Issue 192 <https://github.com/pvcraven/arcade/issues/192>`_: Add function to get closest sprite in a list to another sprite
* `Issue 193 <https://github.com/pvcraven/arcade/issues/193>`_: Improve decorator support

Updated Documentation
~~~~~~~~~~~~~~~~~~~~~

* Link the class methods in the quick index to class method documentation
* Add mountain midpoint displacement example
* Improve CSS
* Add "Two Worlds" example game

Updated Examples
~~~~~~~~~~~~~~~~

* Update ``sprite_collect_coints_move_down.py`` to not use ``all_sprites_list``
* Update ``sprite_bullets_aimed.py`` to add a warning about how to manage text on a scrolling screen
* `Issue 194 <https://github.com/pvcraven/arcade/issues/194>`_: Fix for calculating distance traveled in scrolling examples

Version 1.3.1
-------------

Released 2018-Mar-31

New Features
~~~~~~~~~~~~

* Update ``create_rectangle`` code so that it uses color buffers to improve performance
* `Issue 185 <https://github.com/pvcraven/arcade/issues/185>`_: Add support for repeating textures
* `Issue 186 <https://github.com/pvcraven/arcade/issues/186>`_: Add support for repeating textures on Sprites
* `Issue 184 <https://github.com/pvcraven/arcade/issues/184>`_: Improve sound support
* `Issue 180 <https://github.com/pvcraven/arcade/issues/180>`_: Improve sound support
* Work on improving sound support

Updated Documentation
~~~~~~~~~~~~~~~~~~~~~
* Update quick-links on homepage of http://arcade.academy
* Update Sprite class documentation
* Update copyright date to 2018

Updated Examples
~~~~~~~~~~~~~~~~

* Update PyMunk example code to use keyboard constants rather than hard-coded values
* New sample code showing how to avoid placing coins on walls when randomly placing them
* Improve listing/organization of sample code
* Work at improving sample code, specifically try to avoid using ``all_sprites_list``
* Add PyMunk platformer sample code
* Unsuccessful work at getting TravisCI builds to work
* Add new sample for using shape lists
* Create sample code showing difference in speed when using ShapeLists.
* `Issue 182 <https://github.com/pvcraven/arcade/issues/182>`_: Use explicit imports in sample PyMunk code
* Improve sample code for using a graphic background
* Improve collect coins example
* New sample code for creating caves using cellular automata
* New sample code for creating caves using Binary Space Partitioning
* New sample code for explosions

Version 1.3.0
-------------

Released 2018-February-11.

Enhancements
~~~~~~~~~~~~

* `Issue 126 <https://github.com/pvcraven/arcade/issues/126>`_: Initial support for decorators.
* `Issue 167 <https://github.com/pvcraven/arcade/issues/167>`_: Improve audio support.
* `Issue 169 <https://github.com/pvcraven/arcade/issues/169>`_: Code cleanup in SpriteList.move()
* `Issue 174 <https://github.com/pvcraven/arcade/issues/174>`_: Support for gradients.

Version 1.2.5
-------------

Released 2017-December-29.

Bug Fixes
~~~~~~~~~

* `Issue 173 <https://github.com/pvcraven/arcade/issues/173>`_: JPGs not included in examples

Enhancements
~~~~~~~~~~~~

* `Issue 171 <https://github.com/pvcraven/arcade/issues/171>`_: Clean up sprite list code



Version 1.2.4
-------------

Released 2017-December-23.

Bug Fixes
~~~~~~~~~

* `Issue 170 <https://github.com/pvcraven/arcade/issues/170>`_: Unusually high CPU

Version 1.2.3
-------------

Released 2017-December-20.

Bug Fixes
~~~~~~~~~

* `Issue 44 <https://github.com/pvcraven/arcade/issues/44>`_: Improve wildcard imports
* `Issue 150 <https://github.com/pvcraven/arcade/issues/150>`_: "Shapes" example refers to chapter that does not exist
* `Issue 157 <https://github.com/pvcraven/arcade/issues/157>`_: Different levels example documentation hook is messed up.
* `Issue 160 <https://github.com/pvcraven/arcade/issues/160>`_: sprite_collect_coins example fails to run
* `Issue 163 <https://github.com/pvcraven/arcade/issues/163>`_: Some examples aren't loading images

Enhancements
~~~~~~~~~~~~

* `Issue 84 <https://github.com/pvcraven/arcade/issues/84>`_: Allow quick running via -m
* `Issue 149 <https://github.com/pvcraven/arcade/issues/149>`_: Need better error message with check_for_collision
* `Issue 151 <https://github.com/pvcraven/arcade/issues/151>`_: Need example showing how to go between rooms
* `Issue 152 <https://github.com/pvcraven/arcade/issues/152>`_: Standardize name of main class in examples
* `Issue 154 <https://github.com/pvcraven/arcade/issues/154>`_: Improve GitHub compatibility
* `Issue 155 <https://github.com/pvcraven/arcade/issues/155>`_: Improve readme documentation
* `Issue 156 <https://github.com/pvcraven/arcade/issues/156>`_: Clean up root folder
* `Issue 162 <https://github.com/pvcraven/arcade/issues/162>`_: Add documentation with performance tips
* `Issue 164 <https://github.com/pvcraven/arcade/issues/164>`_: Create option for a static sprite list where we don't check to see if things moved.
* `Issue 165 <https://github.com/pvcraven/arcade/issues/165>`_: Improve error message with physics engine

Version 1.2.2
-------------

Released 2017-December-02.

Bug Fixes
~~~~~~~~~

* `Issue 143 <https://github.com/pvcraven/arcade/issues/143>`_: Error thrown when using scroll wheel
* `Issue 128 <https://github.com/pvcraven/arcade/issues/128>`_: Fix infinite loop in physics engine
* `Issue 127 <https://github.com/pvcraven/arcade/issues/127>`_: Fix bug around warning with Python 3.6 when imported
* `Issue 125 <https://github.com/pvcraven/arcade/issues/125>`_: Fix bug when creating window on Linux

Enhancements
~~~~~~~~~~~~
* `Issue 147 <https://github.com/pvcraven/arcade/issues/147>`_: Fix bug building documentation where two image files where specified incorrectly
* `Issue 146 <https://github.com/pvcraven/arcade/issues/146>`_: Add release notes to documentation
* `Issue 144 <https://github.com/pvcraven/arcade/issues/144>`_: Add code to get window and viewport dimensions
* `Issue 139 <https://github.com/pvcraven/arcade/issues/139>`_: Add documentation on what ``collision_radius`` is
* `Issue 131 <https://github.com/pvcraven/arcade/issues/131>`_: Add example code on how to do full-screen games
* `Issue 113 <https://github.com/pvcraven/arcade/issues/113>`_: Add example code showing enemy turning around when hitting a wall
* `Issue 67 <https://github.com/pvcraven/arcade/issues/67>`_: Improved support and documentation for joystick/game controllers

