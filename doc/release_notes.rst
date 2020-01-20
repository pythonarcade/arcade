:orphan:

.. _release_notes:

Release Notes
=============

Version 2.2.6
-------------

*Release Date: 1/20/2020*

* Bug Fix: particle_fireworks example is not running with 2.2.5 `Issue 555 <https://github.com/pvcraven/arcade/issues/555>`_
* Bug Fix: Sprite.pop isn't reliable `Issue 531 <https://github.com/pvcraven/arcade/issues/531>`_
* Enhancement: Raise error if default font not found on system `Issue 432 <https://github.com/pvcraven/arcade/issues/432>`_
* Enhancement: Add space invaders clone to example list `Issue 526 <https://github.com/pvcraven/arcade/issues/526>`_
* Enhancement: Add sitemap to website
* Enhancement: Improve performance, error handling around setting a sprite's color
* Enhancement: Implement optional filtering parameter to SpriteList.draw `Issue 405 <https://github.com/pvcraven/arcade/issues/405>`_
* Enhancement: Return list of items hit during physics engine update `Issue 401 <https://github.com/pvcraven/arcade/issues/401>`_
* Enhancement: Update resources documentation `Issue 549 <https://github.com/pvcraven/arcade/issues/549>`_
* Enhancement: Add on_update to sprites, which includes delta_time `Issue 266 <https://github.com/pvcraven/arcade/issues/266>`_
* Enhancement: Close enhancement-related github issues and reference them in the new :ref:`enhancement-list`.

Version 2.2.5
-------------

*Release Date: 1/17/2020*

* Enhancement: Improved speed when rendering non-buffered drawing primitives
* Bug fix: Angle working in radians instead of degrees in 2.2.4 `Issue 552 <https://github.com/pvcraven/arcade/issues/552>`_
* Bug fix: Angle and color of sprite not updating in 2.2.4 `Issue 553 <https://github.com/pvcraven/arcade/issues/553>`_


Version 2.2.4
-------------

*Release Date: 1/15/2020*

* Enhancement: Moving sprites now 20% more efficient.

Version 2.2.3
-------------

*Release Date: 1/12/2020*

* Bug fix: Hit boxes not getting updated with rotation and scaling. `Issue 548 <https://github.com/pvcraven/arcade/issues/548>`_
  This update depricates Sprite.points and instead uses Sprint.hit_box and Sprint.get_adjusted_hit_box
* Major internal change around not having ``__init__`` do ``import *`` but
  specifically name everything. `Issue 537 <https://github.com/pvcraven/arcade/issues/537>`_
  This rearranded a lot of files and also reworked the quickindex in documentation.


Version 2.2.2
-------------

*Release Date: 1/9/2020*

* Bug fix: Arcade assumes tiles in tileset are same sized `Issue 550 <https://github.com/pvcraven/arcade/issues/550>`_

Version 2.2.1
-------------

*Release Date: 12/22/2020*

* Bug fix: Resource folder not included in distribution `Issue 541 <https://github.com/pvcraven/arcade/issues/541>`_

Version 2.2.0
-------------

*Release Date: 12/19/2020*

* Major Enhancement: Add built-in resources support `Issue 209 <https://github.com/pvcraven/arcade/issues/209>`_
  This also required many changes to the code samples, but they can be run now without
  downloading separate images.
* Major Enhancement: Auto-calculate hit box points by trimming out the transparency
* Major Enhancement: Sprite sheet support for the tiled map editor works now
* Enhancement: Added ``load_spritesheet`` for loading images from a sprite sheet
* Enhancement: Updates to physics engine to better handle non-rectangular sprites
* Enhancement: Add SpriteSolidColor class, for creating a single-color rectangular sprite
* Enhancement: Expose type hints to modules that depend on arcade via PEP 561
  `Issue 533 <https://github.com/pvcraven/arcade/issues/533>`_
  and `Issue 534 <https://github.com/pvcraven/arcade/issues/534>`_
* Enhancement: Add font_color to gui.TextButton init `Issue 521 <https://github.com/pvcraven/arcade/issues/521>`_
* Enhancement: Improve error messages around loading tilemaps
* Bug fix: Turn on vsync as it sometimes was limiting FPS to 30.
* Bug fix: get_tile_by_gid() incorrectly assumes tile GID cannot exceed tileset length `Issue 527 <https://github.com/pvcraven/arcade/issues/527>`_
* Bug fix: Tiles in object layers not placed properly `Issue 536 <https://github.com/pvcraven/arcade/issues/536>`_
* Bug fix: Typo when loading font `Issue 518 <https://github.com/pvcraven/arcade/issues/518>`_
* Updated ``requirements.txt`` file
* Add robots.txt to documentation

Please also update pyglet, pyglet_ffmpeg2, and pytiled_parser libraries.

Special tanks to Jon Fincher, Mr. Gallo, SirGnip, lubie0kasztanki, and EvgeniyKrysanoc
for their contributions to this release.


Version 2.1.7
-------------

* Enhancement: Tile set support. `Issue 511 <https://github.com/pvcraven/arcade/issues/511>`_
* Bug fix, search file tile images relative to tile map. `Issue 480 <https://github.com/pvcraven/arcade/issues/480>`_


Version 2.1.6
-------------

* Fix: Lots of fixes around positioning and hitboxes with tile maps  `Issue 503 <https://github.com/pvcraven/arcade/issues/503>`_
* Documentation updates, particularly using `on_update` instead of `update` and
  `remove_from_sprite_lists` instead of `kill`. `Issue 381 <https://github.com/pvcraven/arcade/issues/381>`_
* Remove/adjust some examples using csvs for maps

Version 2.1.5
-------------

* Fix: Default font sometimes not pulling on mac  `Issue 488 <https://github.com/pvcraven/arcade/issues/488>`_
* Documentation updates, particularly around examples for animated characters on platformers
* Fix to Sprite class to better support character animation around ladders

Version 2.1.4
-------------

* Fix: Error when importing arcade on Raspberry Pi 4  `Issue 485 <https://github.com/pvcraven/arcade/issues/485>`_
* Fix: Transparency not working in draw functions `Issue 489 <https://github.com/pvcraven/arcade/issues/489>`_
* Fix: Order of parameters in draw_ellipse documentation `Issue 490 <https://github.com/pvcraven/arcade/issues/490>`_
* Raise better error on data classes missing
* Lots of code cleanup from SirGnip `Issue 484 <https://github.com/pvcraven/arcade/pull/484>`_
* New code for buttons and dialog boxes from wamiqurrehman093 `Issue 476 <https://github.com/pvcraven/arcade/pull/476>`_

Version 2.1.3
-------------

* Fix: Ellipses drawn to incorrect dimensions `Issue 479 <https://github.com/pvcraven/arcade/issues/467>`_
* Enhancement: Add unit test for debugging `Issue 478 <https://github.com/pvcraven/arcade/issues/478>`_
* Enhancement: Add more descriptive error when file not found `Issue 472 <https://github.com/pvcraven/arcade/issues/472>`_
* Enhancement: Explicitly state delta time is in seconds `Issue 473 <https://github.com/pvcraven/arcade/issues/473>`_
* Fix: Add missing 'draw' function to view `Issue 470 <https://github.com/pvcraven/arcade/issues/470>`_

Version 2.1.2
-------------

* Fix: Linked to wrong version of Pyglet `Issue 467 <https://github.com/pvcraven/arcade/issues/467>`_

Version 2.1.1
-------------

* Added pytiled-parser as a dependency in setup.py

Version 2.1.0
--------------

* New file reader for tmx files http://arcade.academy/arcade.html#module-arcade.tilemap
* Add new view switching framework http://arcade.academy/examples/index.html#view-management
* Fix and Re-enable TravisCI builds https://travis-ci.org/pvcraven/arcade/builds

* New: Collision methods to Sprite `Issue 434 <https://github.com/pvcraven/arcade/issues/434>`_
* Fix: make_circle_texture `Issue 431 <https://github.com/pvcraven/arcade/issues/431>`_
* Fix: Points drawn as triangles rather than rects `Issue 429 <https://github.com/pvcraven/arcade/issues/429>`_
* Fix: Fix screen update rate issue `Issue 424 <https://github.com/pvcraven/arcade/issues/424>`_
* Fix: Typo `Issue 422 <https://github.com/pvcraven/arcade/issues/422>`_
* Put in exampel Kayzee game
* Fix: Add links to PyCon video `Issue 414 <https://github.com/pvcraven/arcade/issues/414>`_
* Fix: Docstring `Issue 409 <https://github.com/pvcraven/arcade/issues/409>`_
* Fix: Typo `Issue 403 <https://github.com/pvcraven/arcade/issues/403>`_

Thanks to SirGnip, Mr. Gallow, and Christian Clauss for their contributions.

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

