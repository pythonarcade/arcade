
Release Note History
====================

Change log from order Arcade versions.

Version 2.6.17
--------------

*Released 2022-Dec-30*

* Bump Pillow to 9.3.0
* Bump PyMunk to 6.4.0
* Add explicit compatibility tag for 3.11
* Drop 3.7 as part of the test suite

Version 2.6.16
--------------

*Released 2022-Sept-24*

* Support Tiled 1.9 via PyTiled Parser 2.2.0 (`#1324 <https://github.com/pythonarcade/arcade/issues/1324>`_)
* Headless rendering with EGL should now work again
* Fix code highlights in two examples
* Fix data tables in quick index. (`#1312 <https://github.com/pythonarcade/arcade/issues/1312>`_)
* Fix issues running in headless mode
* Update pymunk physics engine to return pre handler (`#1322 <https://github.com/pythonarcade/arcade/issues/1322>`_)
* Bump Pyglet version to 2.0dev23
* Few PEP-8 fixes
* Fix perspective example

*Note:* Development continues on version 2.7, which will be another leap
forward in Arcade development. Feel free to check out the 'development' branch
for the 2.7 changes.

Version 2.6.15
--------------

*Released 2022-Jun-03*

* Pin Pygments version to get around a Pygments/Furo incompatibility.
  (`#1224 <https://github.com/pythonarcade/arcade/issues/1224>`_).
* Fix Google analytics ID
* Bump Pyglet version to 2.0.dev18. (Thanks Pyglet!)
* Fix API colors for Furo theme

Version 2.6.14
--------------

*Released 2022-May-18*

* Various Improvements

  * Allow specifying hit box parameters in :py:func:`~arcade.load_textures` and
    :py:func:`~arcade.load_spritesheet`
  * :py:class:`~arcade.Camera` should no longer apply zoom on the z axis
  * Promote using :py:meth:`arcade.View.on_show_view` in examples
    and tutorials
  * The Arcade window and views now expose :py:meth:`arcade.Window.on_enter`
    :py:meth:`arcade.Window.on_leave`. These events are triggered
    when the mouse enters and leaves the window area.
  * Sections should now also support mouse enter/leave events
  * Hit box calculation methods should raise a more useful
    error message when the texture is not RGBA.
  * Slight optimization in updating sprite location in SpriteList
  * Removed all remaining references to texture transforms
  * Removed the broken ``Sprite.__lt__`` method
  * Added :py:func:`~arcade.get_angle_radians`
  * Removed ``Texture.draw_transformed``
  * Add support for changing the pitch while playing a sound. See the `speed` parameter in
    :py:func:`arcade.play_sound`.
  * Set better blending defaults for Arcade GUI
  * Can now create a texture filled with a single color. See :py:meth:`Texture.create_filled`.
    The Sprite class will use this when creating a solid colored sprite.
  * Bump version numbers of Sphinx, Pillow to current release as of 17-May.
  * Bump Pyglet version to 2.0.dev16. (Thanks Pyglet!)

* Shadertoy

  * Added ``Shadertoy.delta_time`` alias for ``time_delta`` (``iTimeDelta``)
  * Support the ``iFrame`` uniform. Set frame using the
    :py:attr:`arcade.experimental.ShadertoyBase.frame` attribute
  * Support the ``iChannelTime`` uniform. Set time for each individual channel using
    the :py:attr:`arcade.experimental.ShadertoyBase.channel_time` attribute.
  * Support the ``iFrameRate`` uniform. Set frame rate using the
    :py:attr:`arcade.experimental.ShadertoyBase.frame_rate` attribute
  * Support the ``iDate`` uniform. This uniform will be automatically
    set. See :py:meth:`arcade.experimental.ShadertoyBase._get_date`
  * Support the ``iChannelResolution`` uniform. This uniform will be automatically set
  * Added example using video with shadertoy
  * Improve Shadertoy docstrings + unit tests

* Docs / Tutorials / Examples

  * Updated install docs
  * Added tutorial for compiling an Arcade game with Nuitka
  * Improved/extended shadertoy tutorials
  * Added example using textures with shadertoy
  * Added sprite rotation examples
  * Clarified the difference between :py:meth:`arcade.View.on_show_view`
    and :py:meth:`arcade.View.on_show`
  * Improved UIManager docstrings
  * Various annotation and docstring improvements
  * Fixed several broken links in docs
  * We're now building PDF/EPUB docs

* OpenGL

  * Added new method for safely setting shader program uniforms: 
    :py:meth:`arcade.gl.Program.set_uniform_safe`. This method will
    ignore ``KeyError`` if the uniform doesn't exist. This is
    often practical during development because most GLSL compilers/linkers
    will remove uniforms that is determined to not affect the outcome
    of a shader.
  * Added new method for safely setting a uniform array:
    :py:meth:`arcade.gl.Program.set_uniform_array_safe`.
    This is practical during development because uniform arrays
    are in most cases shortened by GLSL compiler if not all
    array indices are used by the shader.
  * Added :py:attr:`arcade.gl.Texture.swizzle`. This can be used
    to reorder how components are read from the texture by a shader
    making it easy to crate simple effects or automatically
    convert BGR pixel formats to RGB when needed.
  * Added ray marching example with fragment shader
  * Allow reading framebuffer data with 2 and 4 byte component sizes
  * Simplified texture atlas texture coordinates to make them
    easier to use in custom shaders.
  * Support dumping the atlas texture as RGB
  * Support dumping the atlas texture with debug lines
    showing texture borders
  * We no longer check ``GL_CONTEXT_PROFILE_MASK`` due to
    missing support in older drivers. Especially GL 3.1 drivers
    that can in theory run arcade
  * Various shader cleanups

* Experimental

  * Added a simple profiler class

Special thanks to
`Vincent Poulailleau <https://github.com/vpoulailleau>`_
`Ian Currie <https://github.com/iansedano>`_
`Mohammad Ibrahim <https://github.com/Ibrahim2750mi>`_,
`pushfoo <https://github.com/pushfoo>`_,
`Alejandro Casanovas <https://github.com/janscas>`_,
`Darren Eberly <https://github.com/Cleptomania>`_,
`pvcraven <https://github.com/pvcraven>`_
and
`Einar Forselv <https://github.com/einarf>`_
for their contributions to this release. Also, thanks to everyone on the Pyglet team! We depend heavily on
Pyglet's continued development.

Version 2.6.13
--------------

*Released 2022-Mar-25*

* New Features

  * Arcade can now run in headless mode on linux servers opening
    more possibilities for users in for example the data science
    community (`#1107 <https://github.com/pythonarcade/arcade/issues/1107>`_).
    See :ref:`headless` for more information.

* Bugfixes

  * The random text glitching issue especially affecting users with iGPUs
    is finally resolved in pyglet. For that reason we have upgraded to
    the pyglet 2.0a2 release.
  * Fixed an issue causing :py:func:`arcade.draw_circle_filled` and
    :py:func:`arcade.draw_circle_outline` to always render with 3 segments
    on some iGPUs.
  * Fixed an issue causing interactive widgets to unnecessarily re-draw when
    hovering or pressing them. This could cause performance issues.
  * SectionManager's ``on_show_view`` was never called when showing a view

* Various Improvements

  * :py:func:`arcade.load_font` now supports resource handles
  * :py:class:`~arcade.PhysicsEngineSimple` can now take an iterable of wall spritelists
  * Sprite creation is now ~6-8% faster.
  * Removed warning about missing shapely on startup
  * Window titles are now optional. If no window title is specified
    the title will be the absolute path to the python file it was created in.
    This was changed because of the new headless mode.
  * Removed ``arcade.quick_run``. This function had no useful purpose.
  * Added clear method to UIManager (`#1116 <https://github.com/pythonarcade/arcade/pull/1116>`_)
  * Updated from Pillow 9.0.0 to 9.0.1

* Tilemap

  * Rectangle objects which are empty(have no width or height) will now be automatically
    converted into single points.
  * The Tile ID of a sprite can be access with ``sprite.properties["tile_id"]``. This refers
    to the local ID of the tile within the Tileset. This value can be used to get the tile info
    for a given Sprite created from loading a tilemap.

* Docs

  * Added python version support info to install instructions (`#1122 <https://github.com/pythonarcade/arcade/pull/1122>`_)
  * Fixed typo in :py:func:`~arcade.Sprite.append_texture` docstring(`#1126 <https://github.com/pythonarcade/arcade/pull/1126>`_)
  * Improved the raycasting tutorial (`#1124 <https://github.com/pythonarcade/arcade/issues/1124>`_)
  * Replace mentions of 3.6 on Linux install page (`#1129 <https://github.com/pythonarcade/arcade/pull/1129>`_)
  * Fix broken links in the homepage (`#1139 <https://github.com/pythonarcade/arcade/pull/1130>`_)
  * Lots of other improvements to docstrings throughout the code base
  * General documentation improvements

* OpenGL

  * :py:class:`arcade.gl.Geometry` now supports transforming to multiple buffers.
  * Added and improved examples in ``experimental/examples``.
  * Major improvements to API docs

Special thanks to
`Mohammad Ibrahim <https://github.com/Ibrahim2750mi>`_,
`pushfoo <https://github.com/pushfoo>`_,
`Alejandro Casanovas <https://github.com/janscas>`_,
`Maic Siemering <https://github.com/eruvanos>`_,
`Cleptomania <https://github.com/Cleptomania>`_,
`pvcraven <https://github.com/pvcraven>`_
and
`einarf <https://github.com/einarf>`_
for their contributions to this release. Also, thanks to everyone on the Pyglet team! We depend heavily on
Pyglet's continued development.

Version 2.6.12
--------------

*Released 2022-Mar-20*

* General:

  * Bugfix: :py:func:`~arcade.check_for_collision_with_list` selected
    the wrong collision algorithm. This could affect performance.
  * Bugfix: GPU collision detection show now work on older MacBooks
  * Added :py:meth:`arcade.Text.draw_debug` that will visualize
    the content area of the text and the anchor point. This
    can be useful to understand the text anchoring.
  * :py:class:`arcade.Text` now has a ``left``, ``right`` ``top``
    and ``bottom`` attribute for getting the pixel locations
    of the content borders.
  * Added performance warning for :py:func:`arcade.draw_text`.
    Using :py:class:`arcade.Text` is a lot faster. We have
    also promoted the use of text objects in examples.
  * Removed the deprecated ``arcade.create_text`` function
  * ``UITextureButton.texture_pressed`` now returns the pressed texture,
    not the texture

* Documentation

  * Work on :ref:`shader_toy_tutorial_glow`.
  * Docstring improvements throughout the code base
  * Many examples are cleaned up

* OpenGL

  * :py:class:`arcade.gl.Buffer` is guaranteed to contain
    zero byte values on creation.
  * Expose :py:class:`~arcade.gl.context.Limits` in :py:attr:`arcade.gl.Context.info`
    and document all limit values
  * Added limit: ``MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS``
  * :py:meth:`arcade.gl.Buffer.read` now reads the correct
    number of bytes when only ``offset`` parameter is passed.
  * Improved compute shader examples
  * Support uniform blocks in compute shaders
  * Bug: :py:attr:`arcade.gl.Context.enabled` now properly
    reverts to the original context flags
  * Many docstring improvements in the ``arcade.gl`` module
  * Bugfix: Query objects ignored creation parameters
  * :py:class:`arcade.gl.ComputeShader` is now part of the gl module
  * :py:class:`arcade.gl.ComputeShader` was added to docs
  * Expose and document :py:class:`arcade.gl.context.ContextStats`

Special thanks to
`MrWardKKHS <https://github.com/MrWardKKHS>`_,
`pvcraven <https://github.com/pvcraven>`_ and
`einarf <https://github.com/einarf>`_
for their contributions to this release. Also, thanks to everyone on the Pyglet team! We depend heavily on
Pyglet's continued development.

Also thanks to:

* `DragonMoffon <https://github.com/DragonMoffon>`_ for arcade.gl testing and feedback
* `bunny-therapist <https://github.com/bunny-therapist>`_ discovering collision bug
* `Robert Morris <https://github.com/morrissimo>`_ for making us aware of the MacBook issue

Version 2.6.11
--------------

*Released 2022-Mar-17*

* Sections - Add support to divide window into sections.
  (Thanks `janscas <https://github.com/janscas>`_ for the contribution.)

  * Add :class:`arcade.Section` to the API.
  * Add :class:`arcade.SectionManager` to the API.
  * Add examples on how to use: :ref:`section_examples`

* New Example Code:

  * Add parallax example: :ref:`background_parallax`.
  * Add GUI flat button styling example: :ref:`gui_flat_button_styled`.
  * Add :ref:`perspective` example.

* New functionality:

  * Add :func:`arcade.get_angle_degrees` function.
  * Add easing functions and example. See :ref:`easing_example_1` and :ref:`easing_example_2`.
  * Add :meth:`arcade.Sprite.facePoint` to face sprite towards a point.

* Fixes:

  * Fixed issue `#1074 <https://github.com/pythonarcade/arcade/issues/1074>`_
    to prevent a crash when opening a window.
  * Fixed issue `#978 <https://github.com/pythonarcade/arcade/issues/978>`_,
    copy button in examples moved to the left to prevent it disappearing.
  * Fixed issue `#967 <https://github.com/pythonarcade/arcade/issues/967>`_,
    CRT example now pulls from resources so people don't have to download image to try it out.
  * PyMunk sample map now in resources so people don't have to download it.
  * :func:`arcade.draw_points` no longer draws the points twice, improving performance.

* Documentation:

  * Update :ref:`pygame-comparison`.
  * Improve ``Sprite.texture`` docs.
  * When building Arcade docs, script now lets us know what classes don't have docstrings.
  * Spelling/typo fixes in docs.

* Misc:

  * Update :class:`arcade.Sprite` to use decorators to declare properties instead of the older method.
  * `#1095 <https://github.com/pythonarcade/arcade/issues/1095>`_,
    Improvements to :class:`arcade.Text` and its documentation.
    We can now also get the pixel size of a Text contents though ``content_width``,
    ``content_height`` and ``content_size``.
  * Force GDI text on windows until direct write is more mature.
  * Optimized text rendering and text rotation
  * :py:func:`arcade.draw_text` and :py:class:`arcade.Text` objects
    now accepts any python object as text and converts it into
    a string internally if needed.
  * :py:class:`~arcade.SpriteList` now exposes several new members
    that used to be private. These are lower level members related
    to the underlying geometry of the spritelist and can be used
    by custom shaders to do interesting things blazingly fast.
    SpriteList interaction example with shaders can be found in the
    experimental directory.
    Members include :py:meth:`~arcade.SpriteList.write_sprite_buffers_to_gpu`,
    :py:attr:`~arcade.SpriteList.geometry`,
    :py:attr:`~arcade.SpriteList.buffer_positions`,
    :py:attr:`~arcade.SpriteList.buffer_sizes`,
    :py:attr:`~arcade.SpriteList.buffer_textures`,
    :py:attr:`~arcade.SpriteList.buffer_colors`,
    :py:attr:`~arcade.SpriteList.buffer_angles` and
    :py:attr:`~arcade.SpriteList.buffer_indices`

* OpenGL:

  * Added support for indirect rendering. This is an OpenGL 4.3 feature.
    It makes us able to render multiple meshes in the the same draw call
    providing significant speed increases in some use cases.
    See :py:meth:`arcade.gl.Geometry.render_indirect` and examples
    in the experimental directory.
  * Added support for unsigned integer uniform types
  * ``arcade.gl.Geometry.transform`` no longer takes a mode parameter.


Special thanks to
`einarf <https://github.com/einarf>`_,
`eruvanos <https://github.com/eruvanos>`_,
`janscas <https://github.com/janscas>`_,
`MrWardKKHS <https://github.com/MrWardKKHS>`_,
`DragonMoffon <https://github.com/DragonMoffon>`_,
`pvcraven <https://github.com/pvcraven>`_,
for their contributions to this release. Also, thanks to everyone on the Pyglet team! We depend heavily on
Pyglet's continued development.

Version 2.6.10
--------------

*Released 2022-Jan-29*

* Sprites

  * Collision checking against one or more sprite lists
    can use the GPU via a 'transform' for much better performance.
    The :meth:`arcade.check_for_collision_with_list` and :meth:`arcade.check_for_collision_with_lists`
    methods now support selection between spatial, GPU, and CPU methods of detection.
  * Added :py:meth:`~arcade.SpriteList.clear` for resetting/clearing a spritelist. This will iterate
    and remove all sprites by default, or do a faster `O(1)` clear. Please read the api docs
    to find out what version fits your use case.
  * :py:class:`~arcade.SpriteList` now supports setting a global color and alpha value.
    The new :py:attr:`~arcade.SpriteList.color`, :py:attr:`~arcade.SpriteList.color_normalized`,
    :py:attr:`~arcade.SpriteList.alpha` and :py:attr:`~arcade.SpriteList.alpha_normalized`
    will affect every sprite in the list. This global color value is multiplied by the
    individual sprite colors. 
  * The :py:class:`~arcade.Sprite` initializer now also accepts ``None`` value for ``hit_box_algorithm``
    in line with the underlying texture method.
  * Fixed a bug causing sprites to have incorrect scale when passing a texture
    during creation.
  * Removed the texture transform feature in sprites. This feature no longer
    makes sense since Arcade 2.6.0 due to the new texture atlas feature.

* Tiled Maps

  * Fixed issue `#1068 <https://github.com/pythonarcade/arcade/issues/1068>`_
    (#1069) where loaded rectangular hit box was wrong.
  * Add better error for infinite tile maps
  * Added ``SpriteList.properties`` and properties from Image and Tile layers will automatically be
    loaded into that when loading a Tiled map

* General

  * ``Window.current_camera`` will now hold a reference to the currently active camera.
    This will be set when calling :py:meth:`arcade.Camera.use`, if no camera is active
    then it will be ``None``.
  * ``Window.clear`` can now clear a sub-section of the screen through
    the new optional ``viewport`` parameter.
  * :py:meth:`arcade.Window.clear` can now take normalized/float color values
  * The new :py:meth:`arcade.View.clear` method now clears the current window. This can
    be used as a shortcut :py:meth:`arcade.Window.clear` when inside of a View class.
  * Add support for custom resource handles
  * Add support for anisotropic filtering with textures.
  * Clearing the window should always clear the entire window
    regardless of camera / viewport setup (unless a scissor box is set)

* Documentation

  * Change examples so instead of ``arcade.start_render()`` we use ``self.clear()``.
    The start render function was confusing people.
    `#1071 <https://github.com/pythonarcade/arcade/issues/1071>`_
  * Fix a bunch of links that were incorrectly pointing to old pvcraven instead of pythonarcade.
    `#1063 <https://github.com/pythonarcade/arcade/issues/1063>`_
  * Update pyinstaller instructions
  * Various documentation improvements and updates

* ``arcade.gl``

  * Fixed a bug were out attributes in transforms was not properly detected
    with geometry shaders
  * Fixed a bug were specifying vertex count wasn't possible with transforms when
    the vertex array has an index buffer bound.
  * The :py:class:`~arcade.gl.Query` object now allows for selecting what specific queries should be performed
  * Fixed a issue causing the wrong garbage collection mode to activate during context creation
  * Viewport values for the default framebuffer now applies pixel ratio by default
  * Scissor values for the default framebuffer now applies pixel ratio by default

* ``arcade.gui``

  * :py:class:`~arcade.gui.UIBoxLayout` supports now align in constructor (changing later requires a `UIBoxLayout.trigger_full_render()`).
  * :py:class:`~arcade.gui.UIBoxLayout` supports now space_between in constructor.
  * :py:class:`~arcade.gui.UIManager` fix #1067, consume press and release mouse events
  * UIManager :py:meth:`~arcade.gui.UIManager.add()` returns added child
  * UILayout :py:meth:`~arcade.gui.UILayout.add()` returns added child
  * UIWidget :py:meth:`~arcade.gui.UIWidget.add()` returns added child
  * New method in UIManager: :py:meth:`~arcade.gui.UIManager.walk_widgets()`
  * New method in UIManager: :py:meth:`~arcade.gui.UIManager.get_widgets_at()`
  * New method in UIWidget: :py:meth:`~arcade.gui.UIWidget.move()`

Special thanks to
`Cleptomania <https://github.com/Cleptomania>`_,
`einarf <https://github.com/einarf>`_,
`eruvanos <https://github.com/eruvanos>`_,
`nrukin <https://github.com/nrukin>`_,
`Jayman2000 <https://github.com/Jayman2000>`_,
`pvcraven <https://github.com/pvcraven>`_,
for their contributions to this release. Also, thanks to everyone on the Pyglet team! We depend heavily on
Pyglet's continued development.

Version 2.6.9
-------------

*Released on 2022-Jan-13*

* Bump version of Pillow from 8.4 to 9.0.0 due to security vulnerability in Pillow.

Version 2.6.8
-------------

*Released on 2021-Dec-25*

* The `Shapely <https://shapely.readthedocs.io/en/latest/>`_ library is now optional.
  The shapely library uses native code to make operations
  such as collision detection and some other geometry operations faster. However they have not
  updated their binaries to support Python 3.10 on macOS and Windows. If Shapely is installed,
  Arcade will use that library. Otherwise it will fall back to slower, but Python-only code.
  See: https://github.com/shapely/shapely/issues/1215
* :class:`~arcade.TileMap` changes:

  There are no API changes to the TileMap class, however full support for TMX maps, TSX tilesets, and TX object templates
  has been added thanks to pytiled-parser 2.0. You should be able to load these formats with 0 change to your code, and use
  all the same features that were available with JSON maps.

  This update also includes the ability to cross-load JSON and TMX maps/tilesets. Meaning you can have a JSON map load a TSX tileset,
  or have a TMX map load a JSON tileset.

  You don't ever need to explicitly set or configure a format to use, it will be automatically determined based on the file you pass
  in. It is determined based on the actual content of the file, and not the filetype, so if you give it a ``.json`` file that actually
  contains TMX, or vice versa, it will still work without problem.

* Update `Pyglet`_ to 2.0.dev13 which fixes a bug where  ``on_resize`` wasn't getting called.
* Added a `compute shader tutorial <https://api.arcade.academy/en/development/tutorials/compute_shader/index.html>`_.

Special thanks to
`Cleptomania <https://github.com/Cleptomania>`_,
`einarf <https://github.com/einarf>`_,
`pvcraven <https://github.com/pvcraven>`_,
for their contributions to this release. Also, thanks to everyone on the Pyglet team! We depend heavily on
Pyglet's continued development.

Version 2.6.7
-------------

*Released on 2021-Dec-15*

* This version updates Pyglet to 2.0dev12. Programs WILL NOT RUN with prior versions of Pyglet.

* :class:`~arcade.Window` changes:

  * Added ``enable_polling`` option to constructor. If enabled then ``window.keyboard`` and ``window.mouse``
    will be activated and able to be used to poll input by accessing them as if they were a dictionary.
    This option is enabled by default. See  `#1038 <https://github.com/pythonarcade/arcade/issues/1038>`_
    
    ``window.keyboard`` can be polled using the values from ``arcade.key``.

    ``window.mouse`` can be polled using the following values:

      * 1: Left click
      * 2: Right click
      * 3: Middle click
      * "x": X position
      * "y": Y position

* :class:`~arcade.Camera` changes:

  * Defaults the viewport width and height to the window size if they are set to 0 now, since you cannot have
    a size of 0 in any direction due to projection calculation. This means that if you do not provide those arguments
    to the constructor it will default to the window size. See  `#1041 <https://github.com/pythonarcade/arcade/issues/1041>`_

* :class:`~arcade.tilemap.TileMap` changes:

  * Added support for layer position offsets. This allows passing a tuple containing an X and Y offset that will be applied to
    each Sprite/Object within the layer. You can set this via an ``offset`` parameter in the ``layer_options`` dict, or you can
    supply a global offset to the map which will be applied to all layers via the ``offset`` parameter of either ``arcade.load_tilemap``
    or to the TileMap constructor directly. Layer specific offsets will override the global default if both are set.
    See  `#1048 <https://github.com/pythonarcade/arcade/issues/1048>`_

  * Added a new error message for JSONDecodeError exceptions, a common problem when tilesets are TSX but maps are JSON.
    This change simply provides a more clear error of the most likely cause of the problem so users don't have to dig as much.

* Text

  * Reverted the extra guards around text rendering that was implemented in 2.6.6. This turned out to cause slowdowns where
    text was being used heavily. Work is still ongoing to fix the remaining issues with text.

* Docs Fixes:

  * See  `#1033 <https://github.com/pythonarcade/arcade/issues/1033>`_ and  `#1046 <https://github.com/pythonarcade/arcade/issues/1046>`_
  * `#1043 <https://github.com/pythonarcade/arcade/issues/1043>`_ Update moving platforms example.

Special thanks to
`Cleptomania <https://github.com/Cleptomania>`_,
`einarf <https://github.com/einarf>`_,
`pvcraven <https://github.com/pvcraven>`_,
`mlr07 <https://github.com/mlr07>`_,
`pushfoo <https://github.com/pushfoo>`_,
for their contributions to this release. Also, thanks to everyone on the Pyglet team! We depend heavily on
Pyglet's continued development.

Version 2.6.6
-------------

*Released on 2021-Dec-04*

* :class:`~arcade.TileMap` changes:

  * Added ``tiled_map`` parameter to init function of TileMap class. It allows to pass an already parsed map from 
    from pytiled-parser to it. Previously it could only be used with raw files and would handle the parsing automatically.
    If a pre-parsed map is passed to this, the ``map_file`` parameter will simply be ignored. This addition makes working
    with pre-parsed maps from a World file possible.

* Text

  * Added extra guards around text rendering calls to hopefully reduce
    glitchy text rendering. Work is still ongoing to fix the remaining issues with text.

* Window:
  
  * Added ``samples`` parameter so user can specify antialiasing quality.
  * The Arcade window should fall back to no antialiasing if the window
    creation fails. Some drivers/hardware don't support it. For example
    when running Arcade in WSL or services like Repl.it.

* SpriteList

  * Optimization: Empty spritelists created before the window or created with ``lazy=True``
    no longer automatically initialize internal OpenGL resources for empty
    spritelists and will instead immediately leave the ``draw()`` method.

* UI

  * Add experimental UI styles dataclasses for UIWidget styling.
  * Add UISlider, which provides a general slider element with some basic functionality
  * Fix UIInputText rendering

* Sound

  * Pyglet audio drivers can now be overridden using the ``ARCADE_SOUND_BACKENDS``
    environment variable for debug purposes. It expects a comma separated string
    with driver names.

* OpenGL

  * From version 2.6.6 Arcade is no longer using the ``auto`` garbage collection
    mode for OpenGL resources. This mode has the same behavior as the Python
    garbage collection. Instead we're now using the ``context_gc`` mode were
    resources are released every time ``Window.flip()`` is called (every frame by default).
    This solves many problems such as threads in your project or external libraries
    suddenly trying to garbage collect OpenGL objects while this is only possible
    in the main thread. This should not cause any problems for most users.
  * Added ``Context.copy_framebuffer``. This can be used to copy framebuffers
    with or without multisampling to another framebuffer. This makes us able
    to do offscreen rendering with multisampling.
  * ``Texture`` s can now be created with multisampling by passing the ``samples``
    parameter. This should only be used for attachments to framebuffers.
    The ``Texture`` object now also has a ``samples`` property (read only).

* Examples

  * Update mini-map example
  * Update scrolling camera example
  * Update google analytics code in docs
  * Remove some less-than-useful examples in the example code section
  * Update platformer example
  * Update windows install instructions
  * Update sample games to show more sample games
  * Improve CRT filter tutorial
  * New example code on how to follow a path
  * Added Game of Life example using shaders

* Documentation

  * Added API docs for ``arcade.gl``
  * ``ArcadeContext`` should now show inherited members
  * Edge artifact page now encourage using ``pixelated`` argument instead of importing
    OpenGL enums from pyglet

Special thanks to
`einarf <https://github.com/einarf>`_,
`pvcraven <https://github.com/pvcraven>`_,
`Cleptomania <https://github.com/Cleptomania>`_,
`eruvanos <https://github.com/eruvanos>`_,
for their contributions to this release. Also, thanks to everyone on the Pyglet team! We depend heavily on
Pyglet's continued development.

Version 2.6.5
-------------

*Released on 2021-Nov-5*

* Increased pyglet's default atlas size for text glyphs to remove text
  flickering and various other artifacts. This issue will be fixed
  in future versions of pyglet.
* Fixed as issue causing all sprites to use the same texture on some Macs.
* Improved doc for setting the viewport.

Special thanks to
`einarf <https://github.com/einarf>`_,
`pushfoo <https://github.com/pushfoo>`_,
for their contributions to this release.

Version 2.6.4
-------------

*Released on 2021-Nov-3*

* Python 3.10 updates. Dependent library versions have been updated to
  include Python 3.10 support. All libraries appear to support 3.10 except
  Shapely 1.8.0 on the Windows platform. Until those binaries are released,
  3.10 support for Windows is still not there.
* :class:`~arcade.SpriteList` additions:

  * A ``visible`` attribute has been added to this class. If set to ``False``, when calling ``draw()`` on the SpriteList it
    will simply return and do nothing. Causing the SpriteList to not be drawn. 
  * SpriteList now has a ``lazy`` (bool) parameter causing it to not create internal OpenGL resources
    until the first draw call or until SpriteList's :meth:`~arcade.SpriteList.initialize` is called. This means that
    sprite lists and sprites can now be created in threads.
  * Fixes/optimized :py:meth:`~arcade.SpriteList.reverse` and :py:meth:`~arcade.SpriteList.shuffle` methods.
  * Added :py:meth:`~arcade.SpriteList.sort` method. This is identical to Python's ``list.sort``
    but are many times faster sorting your sprites.
  * Removed noisy warning message when spritelists were created before the window
  * Fixed an issue with :py:meth:`~arcade.SpriteList.insert` when trying to insert sprites past
    an index greater than the current length. It could cause inserted sprites to be invisible.

* :class:`~arcade.Sprite` changes:

  * Added :py:attr:`arcade.Sprite.visible` property for quickly making sprites visible/invisible. This is simply
    a shortcut for changing the alpha value.
  * Optimization: Sprites should now take ~15% less memory and be ~15% faster to create
  * :py:class:`~arcade.SpriteCircle` and :py:class:`SpriteSolidColor` textures are now cached internally
    for better performance.

* :class:`~arcade.PhysicsEnginePlatformer` Optimization:

  A ``walls`` parameter has been added to this class. The new intention for usage of this class is for static(non-moving)
  sprites to be sent to the ``walls`` parameter, while moving platforms should be sent to the ``platforms`` parameter. Properly
  differentiating between these parameters can result in extreme performance benefits. Sprites added to ``platforms`` are
  O(n) whereas Sprites added to ``walls`` are O(1). This has been tested with anywhere from 100 to 500k+ Sprites, and the
  physics engine shows no measurable difference between those scenarios.

  We have also removed the ability to send a single Sprite to the ``platforms``, ``ladders``, and ``walls`` parameters of this class.
  This is a use case which results in some improper usage and unnecessary slowdowns. These parameters will now only accept SpriteLists
  or an iterable such as a list containing SpriteLists. If you are currently using this functionality, you just need to add your Sprite
  to a SpriteList and provide that instead.

  The simple platformer tutorial has already been updated to make use of this optimization.

* :class:`~arcade.Scene` is additions:

  * The Scene class is now sub-scriptable, previously in order to retrieve a SpriteList from Scene, you needed to use
    either ``Scene.name_mapping`` or ``Scene.get_sprite_list``.
    We have now added the ability to access it by sub-scripting the Scene object directly, like
    ``spritelist = my_scene["My Layer"]``
  * Added ``on_update()`` method. Previously Scene only had ``update()``. Both of these methods simply call the
    corresponding one on each SpriteList, however previously you could not
    do this with ``on_update()``. The difference between these methods is that ``on_update()`` allows passing a delta
    time, whereas ``update()`` does not.

* :class:`~arcade.TileMap` additions and fixes:

  * When loading a Tiled map Arcade will now respect if layers are visible or not. If a layer is not visible in Tiled,
    the SpriteList
    created for it will use the new ``visible`` attribute to control it. This means that when creating a Scene from a
    TileMap, this will
    automatically be respected as well.
  * Fixed support for parallax values on layers. Currently there is no support to do anything with these out of the box,
    you'd need to manually
    pull the values and do something based on them, however previously the map would not load if the values were changed
    from the default. This has
    been fixed in pytiled-parser and we have updated our version in Arcade accordingly.
  * Removed a lingering debug tactic of printing the class name of custom SpriteList classes when loading a TileMap.

* UI

  * :class:`~arcade.UIInputText` now supports both RGB and RGBA text color

* Text
  
  * Several text related bugs have been resolved in pyglet, the underlying library
    we now use for text drawing. This has been a fairly time consuming task
    over several weeks and we hope the new pyglet based text system will stabilize from now on.
    Arcade is an early adopter of pyglet 2.0 currently using a pre-release
  * The :py:class:`~arcade.Text` object is now usable and is preferred over
    :py:func:`arcade.draw_text` in many cases for performance reasons.
  * Text related functions should now have better documentation

* Misc:

  * Added support to the :class:`~arcade.View` class for :meth:`~arcade.View.on_resize`
  * Many docstring improvements. Initializer docstrings have now been moved to the class
    docstring ensuring they will always show up in the generated api docs.
  * Added some new sections under advanced docs related to OpenGL, textures and texture atlas
  * New utility function :func:`~arcade.color_from_hex_string` that will turn a hex string into a color.
  * Bug: Removed a lingering debug key ``F12`` that showed the contents of the global texture atlas
  * Several improvements to typing and PEP-8. Plus automated tests to help keep things
    in good shape.
  * Added ``run()`` shortcut in ``arcade.Window``. Usage: ``MyWindow().run()``
  * Addition of :class:`~arcade.PymunkException` class for throwing Pymunk errors in the
    Pymunk physics engine.
  * The :func:`~arcade.check_for_collision_with_lists` function will now accept any Iterable(List, Tuple, Set, etc) containing SpriteLists.

* Lower level rendering API:

  * Fixed a problem causing Geometry / VertexArray to ignore ``POINTS`` primitive mode when this is set as default.
  * Added support for compute shaders. We support writing to textures and SSBOs (buffers).
    Examples can be found in ``arcade/experimental/examples``
  * Fixed a crash when drawing with geometry shaders due to referencing a non-existent enum

Special thanks to
`einarf <https://github.com/einarf>`_,
`pvcraven <https://github.com/pvcraven>`_,
`pushfoo <https://github.com/pushfoo>`_,
`Cleptomania <https://github.com/Cleptomania>`_,
`Olliroxx <https://github.com/Olliroxx>`_,
`mlr07 <https://github.com/mlr07>`_,
`yegarti <https://github.com/yegarti>`_,
`Jayman2000 <https://github.com/Jayman2000>`_
for their contributions to this release.

Special thanks to `Benjamin <https://github.com/benmoran56>`_ and `caffeinepills <https://github.com/caffeinepills>`_
for their help to squash bugs in pyglet 2.0.

Version 2.6.3
-------------

*Released on 2021-Sept-21*

* Bug fix, use a signed in as the 'killed' index. `#965 <https://github.com/pythonarcade/arcade/issues/965>`_
* Fix dead links on getting started page See `#960 <https://github.com/pythonarcade/arcade/issues/960>`_
* Fix some doc language that mixed function/method vocabulary. See `#963 <https://github.com/pythonarcade/arcade/issues/963>`_
* Some initial work on compute and camera shader work. Not done yet.
* Fixed a bug causing the sprite geometry shader to not compile in some platforms
* Fixed a bug related to texture bleeding with sprites. Texture atlases now
  pad the texture borders with repeating pixel data to combat this. It should make sprites
  look much better when scrolling, zooming and on hidpi displays.
  `#959 <https://github.com/pythonarcade/arcade/issues/959>`_
* Added hack for some gui text not appearing (pyglet 2.0 bug)
* UIMessageBox should now respect the width and height of the widget
* ``SpriteList.draw``: Added ``pixelated`` (bool) argument as a shortcut to setting nearest interpolation
* ``SpriteList.draw``: The arguments are now better exposed in docs
* ``Sprite.draw`` now has the same blending and interpolation argument as ``SpriteList.draw``
* Upgraded to pyglet 2.0dev9

Version 2.6.2
-------------

*Released on 2021-Sept-18*

* Support for custom classes that subclass Sprite for tiles in TileMap objects. See `#942 <https://github.com/pythonarcade/arcade/issues/942>`_
* Update PymunkPhysicsEngine to work with any direction of gravity rather than just downward. See `#940 <https://github.com/pythonarcade/arcade/issues/940>`_
* Update library versions we depend on. PIL, Pymunk, etc.
* Fix the card game example code. See `#951 <https://github.com/pythonarcade/arcade/issues/951>`_
* Fix for drawing small circles not using enough segments. See `#950 <https://github.com/pythonarcade/arcade/issues/950>`_
* A lot of documentation links in the .py files were old and not updated to the RTD way, fixed now.
* ``arcade.key`` was missing from the documentation quick index. Fixed.
* Fixed a rendering issue with sprites on M1 Macs
* Fix caret not showing up in input box
* Lots of type-hint fixes

Version 2.6.1
-------------

Fixes
~~~~~

* Removed type annotations which were introduced in Python 3.8 to fix compatibility with Python 3.7 and 3.6
* Fixed flickering on static drawing. See `#858 <https://github.com/pythonarcade/arcade/issues/858>`_

Version 2.6.0
-------------

Version 2.6.0 is a major update to Arcade. It is not 100% backwards compatible with the 2.5 API.
Updates were made to text rendering, tiled map support, sprites, shaders, textures, GUI system,
and the documentation.

* `Tiled Map Editor <https://www.mapeditor.org/>`_ support has been overhauled.

  * Arcade now uses the .json file format for maps created by the Tiled Map Editor rather than the TMX format.
    Tile sets and other supporting files need to all be saved in .json format. The XML based formats are no longer
    supported by Arcade.
  * Arcade now supports a minimum version of Tiled 1.5. Maps saved with an older version of Tiled will likely work
    in most scenarios, but for all features the minimum version we can support is 1.5 due to changes in the Tiled
    map format.
  * Feature-support for Tiled maps has been improved to have near 100% parity with Tiled itself.
  * See :ref:`platformer_tutorial` for a how-to, Tiled usage starts at Chapter 9.
  * See `Community RPG <https://github.com/pythonarcade/community-rpg>`_ or `Community Platformer <https://github.com/pythonarcade/community-platformer>`_ for a more complex example program.

  .. image:: https://raw.githubusercontent.com/pythonarcade/community-rpg/main/screenshot.png
     :width: 50%
     :alt: Screenshot of tile map

* Texture atlases have been introduced, texture management has been improved.

  * A sprite list will create and use its own texture atlas.
  * This introduces a new :class:`arcade.TextureAtlas` class that is used internally by SpriteList.
  * Sprites with new textures can be added to a sprite list without the delay. Arcade 2.5 had a delay caused by rebuilding
    its internal sprite sheet.
  * As a side effect, sprites can only belong to one sprite list that renders.
  * The texture atlas portion of a sprite can be drawn to, and quickly updated on the GPU side.

    * To demonstrate, there is a new :ref:`minimap` example that creates a sprite that has a dynamic minimap
      projected onto it.

    .. image:: ../example_code/images/minimap.png
       :width: 50%
       :alt: Screenshot of minimap

* Revamped text rendering done by :func:`arcade.draw_text`.
  Rather than use Pillow to render onto an image, Arcade uses Pyglet's
  text drawing system.
  Text drawing is faster, higher resolution, and not prone to memory leaks. Fonts are now specifed by the
  font name, rather than the file name of the font.

  * Fonts can be dynamically loaded with :func:`arcade.load_font`.
  * Kenney.nl's TTF are now included as build-in resources.
  * See the :ref:`drawing_text` example.

  .. image:: ../example_code/images/drawing_text.png
     :width: 50%
     :alt: Screenshot of drawing text

* SpriteList optimizations.

  * Sprites now draw even faster than before. On an Intel i7 with nVidia 980 Ti graphics card,
    8,000+ moving sprites can be drawn while maintaining 60 FPS. The same machine can only
    do 2,000 sprites with Pygame before FPS drops.

* Shadertoy support.

  * `Shadertoy.com <https://www.shadertoy.com/>`_ is a website that makes it easier to write OpenGL shaders.
  * The new :class:`arcade.Shadertoy` class makes it easy to run and interact with these shaders in Arcade.
  * See :ref:`shader_toy_tutorial_glow` and `Asteroids <https://github.com/pythonarcade/asteroids>`_.

    .. image:: ../tutorials/shader_toy_glow/cyber_fuji_2020.png
       :width: 40%

    .. image:: ../tutorials/shader_toy_glow/star_nest.png
       :width: 40%

* Reworked GUI

    .. image:: ../example_code/images/gui_flat_button.png
       :width: 40%

    .. image:: ../example_code/images/gui_widgets.png
       :width: 40%

    .. image:: ../example_code/images/gui_ok_messagebox.png
       :width: 40%

  * UIElements are replaced by UIWidgets
  * Option to relative pin widgets on screen to center or border (supports resizing)
  * Widgets can be placed on top of each other
  * Overlapping widgets properly handle mouse interaction
  * Fully typed event classes
  * Events contain source widget
  * ScrollableText widgets (more to come)
  * Support for Sprites within Widgets
  * Declarative coding style for borders and padding `widget.with_border(...)`
  * Automatically place widgets vertically or horizontally (`UIBoxLayout`)
  * Dropped support for YAML style files
  * Better performance and limited memory usage
  * More documentation (:ref:`gui_concepts`)
  * Available Elements:

    * :class:`~arcade.gui.UIWidget`:

      * :class:`~arcade.gui.UIFlatButton` - 2D flat button for simple interactions (hover, press, release, click)
      * :class:`~arcade.gui.UITextureButton` - textured button (use :meth:`arcade.load_texture()`) for simple interactions (hover, press, release, click)
      * :class:`~arcade.gui.UILabel` - Simple text, supports multiline
      * :class:`~arcade.gui.UIInputText` - field to accept user text input
      * :class:`~arcade.gui.UITextArea` - Multiline scrollable text widget.
      * :class:`~arcade.gui.UISpriteWidget` - Embeds a Sprite within the GUI tree

    * :class:`~arcade.gui.UILayout`:

        * :class:`~arcade.gui.UIBoxLayout` - Places widgets next to each other (vertical or horizontal)

    * :class:`~arcade.gui.UIWrapper`:

        * :class:`~arcade.gui.UIPadding` - Add space around a widget
        * :class:`~arcade.gui.UIBorder` - Add border around a widget
        * :class:`~arcade.gui.UIAnchorWidget` - Used to position UIWidgets relative on screen

    * Constructs

        * :class:`~arcade.gui.UIMessageBox` - Popup box with a message text and a few buttons.

    * Mixins

        * :class:`~arcade.gui.mixins.UIDraggableMixin` - Makes a widget draggable.
        * :class:`~arcade.gui.mixins.UIMouseFilterMixin` - Catches mouse events that occure within the widget boundaries.
        * :class:`~arcade.gui.mixins.UIWindowLikeMixin` - Combination of :class:`~arcade.gui.mixins.UIDraggableMixin` and :class:`~arcade.gui.UIMouseFilterMixin`.

  * WIP
    * UIWidgets contain information about preferred sizes
    * UILayouts can grow or shrink widgets, to adjust to different screen sizes

* Scene Manager.

  * There is now a new :class:`arcade.Scene` class that can be used to manage SpriteLists and their draw order.
    This can be used in place of having to draw multiple spritelists in your draw function. 
  * Contains special integration with :class:`arcade.TileMap` using :func:`arcade.Scene.from_tilemap` which will
    automatically create an entire scene from a loaded tilemap in the proper draw order.
  * See :ref:`platformer_tutorial` for an introduction to this concept, and it is used heavily throughout that tutorial.

* Camera support

  * Easy scrolling with :class:`arcade.Camera`
  * For an example of this see the example: :ref:`sprite_move_scrolling`.
  * Automatic camera shake can be added in, see the example: :ref:`sprite_move_scrolling_shake`.
  * Several other examples and tutorials make use of this class, like :ref:`platformer_tutorial`.

* Add a set of functions to track performance statistics. See :ref:`perf_info_api`.
* Added the class :class:`arcade.PerfGraph`, a subclass of Sprite that will graph FPS or time to process a dispatch-able
  event line 'update' or 'on_draw'.

  .. image:: ../example_code/images/performance_statistics.png
     :width: 50%
     :alt: Screenshot of performance statistics

* Documentation

  * Lots of individual documentation updates for commands.
  * The :ref:`quick_index` has been reorganized to be easier to find commands, and
    the individual API documentation pages have been broken into parts, so it isn't one large monolithic page.
  * New tutorial for :ref:`raycasting_tutorial`.

    .. image:: ../tutorials/raycasting/example.png
       :width: 50%

  * New tutorial for :ref:`shader_toy_tutorial_glow`.
  * Revamped tutorial: :ref:`platformer_tutorial`.
  * Revamped minimap example: :ref:`minimap`.
  * Moved from AWS hosting to read-the-docs hosting so we can support multiple versions of docs.
  * New example showing how to use the new performance statistics API: :ref:`performance_statistics_example`
  * New example: :ref:`gui_widgets`
  * New example: :ref:`gui_flat_button`
  * New example: :ref:`gui_ok_messagebox`

* API commands

   * :func:`arcade.get_pixel` supports getting RGB and RGBA color value
   * :func:`arcade.get_three_color_float` Returns colors as RGB float with numbers 0.0-1.1 for each color
   * :func:`arcade.get_four_color_float`  Returns colors as RGBA float with numbers 0.0-1.1 for each color\

* Better PyInstaller Support

  Previously our PyInstaller hook only fully functioned on Windows, with a bit of functionality on Linux.
  Mac was just completely unsupported and would raise an UnimplementedError if you tried.

  Now we have full out of the box support for PyInstaller with Windows, Mac, and Linux.

  See :ref:`bundle_into_redistributable` for an example of how to use it.

* Sound

  The sound API remains unchanged, however general stability of the sound system has been greatly improved via
  updates to `Pyglet <http://pyglet.org/>`_.

* `Fix for A-star path finding routing through walls <https://github.com/pythonarcade/arcade/issues/806>`_

Special thanks to:

* `einarf <https://github.com/einarf>`_ for performance improvements, texture atlas support, shader toy support,
  text drawing support, advice on GUI, and more.
* `Cleptomania <https://github.com/Cleptomania>`_ for Tiled Map support, sound support, and more.
* `eruvanos <https://github.com/eruvanos>`_ for the original GUI and all the GUI updates.
* `benmoran56 <https://github.com/benmoran56>`_ and everyone that contributes to the excellent
  `Pyglet <http://pyglet.org/>`_ library we use so much.

Version 2.5.7
-------------

*Released on 2021-May-25*

Fixes
~~~~~

* The Arcade gui should now respect the current viewport
* Fixed an issue with UILabel allocating large amounts of
  textures over time consuming a lot of memory
* Fixed an issue with the initial viewport sometimes being
  1 pixel too small causing some artifacts
* Fixed a race condition in ``Sound.stop()`` sometimes
  causing a crash
* Fixed an issue in requirements causing issues for poetry
* Fixed an error reporting issue when reaching maximum
  texture size

New Features
~~~~~~~~~~~~

**replit.com**

Arcade should now work out of the box on replit.com. We detect
when Arcade runs in replit tweaking various settings. One important
setting we disable is antialiasing since this doesn't work
well with software rendering.

**Alternative Garbage Collection of OpenGL Resources**

``arcade.gl.Context`` now supports an alternative garbage collection mode more
compatible with threaded applications and garbage collection of OpenGL resources.
OpenGL resources can only be accessed or destroyed from the same thread the
window was created. In threaded applications the Python garbage collector
can in some cases try to destroy OpenGL objects possibly causing a hard crash.

This can be configured when creating the ``arcade.Window`` passing in a new
``gc_mode`` parameter. By default this parameter is ``"auto"`` providing
the default garbage collection we have in Python.

Passing in ``"context_gc"`` on the other hand will move all "dead" OpenGL
objects into ``Context.objects``. These can be garbage collected manually
by calling ``Context.gc()`` in a more controlled way in the the right thread.

Version 2.5.6
-------------

Version 2.5.6 was released 2021-03-28

* Fix issue with PyInstaller and Pymunk not allowing Arcade to work with bundling
* `Fix some PyMunk examples <https://github.com/pythonarcade/arcade/issues/835>`_
* Update some example code. Highlight PyInstaller instructions

Version 2.5.5
-------------

Version 2.5.5 was released 2021-02-23

* `Fix setting an individual sprite list location to a new sprite not working <https://github.com/pythonarcade/arcade/issues/824>`_

Version 2.5.4
-------------

Version 2.5.4 was released 2021-02-19

* `Fix for soloud installer hook <https://github.com/pythonarcade/arcade/issues/816>`_
* Add fishy game on example page
* Fix but around framebuffer creation not properly restoring active frame buffer
* Fix for but where TextureRenderTarget creates FBO twice
* Updated pinned version numbers for dependent libraries
* MyPy fixes
* Minor improvements around SpriteList list operations
* `Fix for physics engine getting stuck on a corner <https://github.com/pythonarcade/arcade/issues/820>`_


Version 2.5.3
-------------

Version 2.5.3 was released 2021-01-27

* `Fix memory leak when removing sprites from sprite list <https://github.com/pythonarcade/arcade/issues/815>`_
* `Fix solitaire example using old hitbox parameter <https://github.com/pythonarcade/arcade/issues/814>`_
* Fix/improve tetris example
* Fix for camera2d.scroll_x

Version 2.5.2
-------------

Version 2.5.2 was released 2020-12-27

* Improve schedule/unschedule docstrings
* Fix Sound.get_length
* Raise error if there are multiple instances of a streaming source
* Fix background music example to match new sound API
* Update main landing page for docs
* Split sprite platformer tutorial into multiple pages
* Add 'related projects' page
* Add 'adventure' sample game link
* Add resources for top-down tank images
* Add turn-and-move example
* Fix name of sandCorner_left.png
* Update tilemap to error out instead of continuing if we can't find a tile
* Improve view tutorial
* Generate error rather than warning if we can't find image or sound file
* Specify timer resolution in Windows

Version 2.5.1
-------------

Version 2.5.1 was released 2020-12-14

* Fix bug with sound where panning wasn't working on Windows machines.
* `Fix for create_lines_with_colors <https://github.com/pythonarcade/arcade/issues/804>`_
* `Fix for pegboard example, coin image too small <https://github.com/pythonarcade/arcade/issues/779>`_
* `Fix for create_ellipse dimensions being too big. <https://github.com/pythonarcade/arcade/issues/756>`_
* `Add visible kwarg to window constructor <https://github.com/pythonarcade/arcade/pull/802>`_
* Fix some type-checking errors found by mypy.
* Update API docs

Version 2.5
-----------

Version 2.5 was released 2020-12-09

(Note, libraries Arcade depends on do not work yet with Python 3.9 on Mac. Mac
users will need to use Python 3.6, 3.7 or 3.8.)

* `Changing to Pyglet from Soloud for Sound <https://github.com/pythonarcade/arcade/pull/746>`_
* `Optimize has_line_of_sight using shapely <https://github.com/pythonarcade/arcade/pull/783>`_
* `Update setuptools configuration to align with PEP 517/518 <https://github.com/pythonarcade/arcade/pull/780>`_
* `Changed algorithm for checking for polygon collisions <https://github.com/pythonarcade/arcade/issues/771>`_
* `Fix incorrect PyInstaller data file path handling docs <https://github.com/pythonarcade/arcade/pull/774>`_
* `Fix for hitbox not scaling <https://github.com/pythonarcade/arcade/issues/752>`_
* `Add support for pyinstaller on Linux <https://github.com/pythonarcade/arcade/issues/800>`_

General

* `SpriteList.draw now supports a blend_function parameter. <https://github.com/pythonarcade/arcade/pull/770>`_
  This opens up for drawing sprites with different blend modes.
* Bugfix: Sprite hit box didn't properly update when changing width or height
* GUI improvements (eruvanos needs to elaborate)
* Several examples was improved
* Improvements to the pyinstaller tutorial
* Better pin versions of depended libraries
* Fix issues with simple and platformer physics engines.

Advanced

* Added support for tessellation shaders
* ``arcade.Window`` now takes a ``gl_version`` parameter
  so users can request a higher OpenGL version than the
  default ``(3, 3)`` version. This only be used to advanced users.
* Bugfix: Geometry's internal vertex count was incorrect when using an index buffer
* We now support 8, 16 and 32 bit index buffers
* Optimized several draw methods by omitting ``tobytes()`` letting
  the buffer protocol do the work
* More advanced examples was added to ``arcade/experimental/examples``

Documentation

* Add :ref:`conway_alpha` example showing how to use alpha to control display
  of sprites in a grid.
* Improve documentation around sound API.
* Improve documentation with FPS and timing stats example.
* Improve moving platform docs a bit in :ref:`platformer_tutorial` tutorial.

Version 2.4.3
-------------

Version 2.4.3 was released 2020-09-30

General

* Added PyInstalled hook and tutorial
* ShapeLists should no longer share position between instances
* GUI improvements: new UIImageToggle

Low level rendering API (arcade.gl):

* ArcadeContext now has a load_texture method for creating opengl textures using Pillow.
* Bug: Fixed an issue related to drawing indexed geometry with offset
* Bug: Scissor box not updating when using framebuffer
* Bug: Fixed an issue with pack/unpack alignment for textures
* Bug: Transforming geometry into a target buffer should now work with byte offset
* Bug: Duplicate sprites in 'check_for_collision_with_list' `Issue #763 <https://github.com/pythonarcade/arcade/issues/763>`_
* Improved docstrings in arcade.gl

Version 2.4.2
-------------

Version 2.4.2 was released 2020-09-08

* Enhancement: ``draw_hit_boxes`` new method in ``SpriteList``.
* Enhancement: ``draw_points`` now significantly faster
* Added UIToggle, on/off switch
* Add example showing how to do GPU transformations with the mouse
* Create buttons with default size/position so size can be set after creation.
* Allow checking if a sound is done playing `Issue 728 <https://github.com/pvcraven/arcade/issues/728>`_
* Add an early camera mock-up
* Add ``finish`` method to ``arcade.gl.context``.
* New example arcade.experimental.examples.3d_cube (experimental)
* New example arcade.examples.camera_example
* Improved UIManager.unregister_handlers(), improves multi view setup

* Update ``preload_textures`` method of ``SpriteList`` to actually pre-load textures
* GUI code clean-up `Issue 723 <https://github.com/pvcraven/arcade/issues/723>`_
* Update downloadable .zip for for platformer example code to match current code in documentation.
* Bug Fix: ``draw_point`` calculates wrong point size
* Fixed draw_points calculates wrong point size
* Fixed create_line_loop for thickness !=
* Fixed pixel scale for offscreen framebuffers and read()
* Fixed SpriteList iterator is stateful
* Fix for pixel scale in offscreen framebuffers
* Fix for UI tests
* Fix issues with FBO binding
* Cleanup Remove old examples and code


Version 2.4
-----------

Arcade 2.4.1 was released 2020-07-13.

Arcade version 2.4 is a major enhancement release to Arcade.

.. image:: ../example_code/images/light_demo.png
    :width: 30%
    :class: inline-image
    :target: examples/light_demo.html

.. image:: ../example_code/images/astar_pathfinding.png
    :width: 30%
    :class: inline-image
    :target: examples/astar_pathfinding.html

.. image:: ../tutorials/pymunk_platformer/title_animated_gif.gif
    :width: 30%
    :class: inline-image
    :target: tutorials/pymunk_platformer/index.html

.. image:: ../tutorials/gpu_particle_burst/explosions.gif
    :width: 30%
    :class: inline-image
    :target: tutorials/gpu_particle_burst/index.html

.. image:: ../tutorials/card_game/animated.gif
    :width: 30%
    :class: inline-image
    :target: tutorials/card_game/index.html

.. image:: ../example_code/images/transform_feedback.png
    :width: 30%
    :class: inline-image
    :target: examples/transform_feedback.html

Version 2.4 Major Features
~~~~~~~~~~~~~~~~~~~~~~~~~~

* Support for defining your own frame buffers, shaders, and more
  advanced OpenGL programming. New API in Arcade Open GL.

    * Support to render to frame buffer, then re-render.
    * Use frame buffers to create a 'glow' or 'bloom' effect
    * Use frame-buffers to support lights: :ref:`light_demo`.

* New support for style-able GUI elements.
* PyMunk engine for platformers. See tutorial: :ref:`pymunk_platformer_tutorial`.
* AStar algorithm for finding paths. See
  :data:`~arcade.astar_calculate_path` and :data:`~arcade.AStarBarrierList`.

  * For an example of using the A-Star algorithm, see :ref:`astar_pathfinding`.


Version 2.4 Minor Features
~~~~~~~~~~~~~~~~~~~~~~~~~~

**New functions/classes:**

* Added `get_display_size() <arcade.html#arcade.get_display_size>`_ to get
  resolution of the monitor
* Added `Window.center_window() <arcade.html#arcade.Window.center_window>`_ to
  center the window on the monitor.
* Added `has_line_of_sight() <arcade.html#arcade.has_line_of_sight>`_ to
  calculate if there is line-of-sight between two points.
* Added `SpriteSolidColor <arcade.html#arcade.SpriteSolidColor>`_
  class that makes a solid-color rectangular sprite.
* Added `SpriteCircle <arcade.html#arcade.SpriteCircle>`_
  class that makes a circular sprite, either solid or with a fading gradient.
* Added :data:`~arcade.get_distance` function to get the distance between two points.

**New functionality:**

* Support for logging. See :ref:`logging`.
* Support volume and pan arguments in `play_sound <arcade.html#arcade.play_sound>`_
* Add ability to directly assign items in a sprite list. This is particularly
  useful when re-ordering sprites for drawing.
* Support left/right/rotated sprites in tmx maps generated by the Tiled Map Editor.
* Support getting tmx layer by path, making it less likely reading in a tmx file
  will have directory confusion issues.
* Add in font searching code if we can't find default font when drawing text.
* Added :data:`arcade.Sprite.draw_hit_box` method to draw a hit box outline.
* The :data:`arcade.Texture` class, :data:`arcade.Sprite` class, and
  :data:`arcade.tilemap.process_layer` take in ``hit_box_algorithm`` and
  ``hit_box_detail`` parameters for hit box calculation.

.. figure:: ../api_docs/images/hit_box_algorithm_none.png
   :width: 40%

   hit_box_algorithm = "None"

.. figure:: ../api_docs/images/hit_box_algorithm_simple.png
   :width: 55%

   hit_box_algorithm = "Simple"

.. figure:: ../api_docs/images/hit_box_algorithm_detailed.png
   :width: 75%

   hit_box_algorithm = "Detailed"


Version 2.4 Under-the-hood improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**General**

* Simple Physics engine is less likely to 'glitch' out.
* Anti-aliasing should now work on windows if ``antialiasing=True``
  is passed in the window constructor.
* Major speed improvements to drawing of shape primitives, such as lines, squares,
  and circles by moving more of the work to the graphics processor.
* Speed improvements for sprites including gpu-based sprite culling (don't draw sprites outside the screen).
* Speed improvements due to shader caching. This should be especially noticeable on Mac OS.
* Speed improvements due to more efficient ways of setting rendering states such as projection.
* Speed improvements due to less memory copying in the lower level rendering API.

**OpenGL API**

A brand new low level rendering API wrapping OpenGL 3.3 core was added in this release.
It's loosely based on the `ModernGL <https://github.com/moderngl/moderngl>`_ API,
so ModernGL users should be able to pick it up fast.
This API is used by Arcade for all the higher level drawing functionality, but
can also be used by end users to really take advantage of their GPU. More
guides and tutorials around this is likely to appear in the future.

A simplified list of features in the new API:

* A :py:class:`~arcade.gl.Context` and :py:class:`arcade.ArcadeContext` object was
  introduced and can be found through the ``window.ctx`` property.
  This object offers methods to create opengl resources such as textures,
  programs/shaders, framebuffers, buffers and queries. It also has shortcuts for changing
  various context states. When working with OpenGL in Arcade you are encouraged to use
  ``arcade.gl`` instead of ``pyglet.gl``. This is important as the context is doing
  quite a bit of bookkeeping to make our life easier.
* New :py:class:`~arcade.gl.Texture` class supporting a wide variety of formats such as 8/16/32 bit
  integer, unsigned integer and float values. New convenient methods and properties
  was also added to change filtering, repeat mode, read and write data, building mipmaps etc.
* New :py:class:`~arcade.gl.Buffer` class with methods for manipulating data such as
  simple reading/writing and copying data from other buffers. This buffer can also
  now be bound as a uniform buffer object.
* New :py:class:`~arcade.gl.Framebuffer` wrapper class making us able to render any content into
  one more more textures. This opens up for a lot of possibilities.
* The :py:class:`~arcade.gl.Program` has been expanded to support geometry shaders and transform feedback
  (rendering to a buffer instead of a screen). It also exposes a lot of new
  properties due to much more details introspection during creation.
  We also able to assign binding locations for uniform blocks.
* A simple glsl wrapper/parser was introduced to sanity check the glsl code,
  inject preprocessor values and auto detect out attributes (used in transforms).
* A higher level type :py:class:`~arcade.gl.Geometry` was introduced to make working with
  shaders/programs a lot easier. It supports using a subset of attributes
  defined in your buffer description by inspecting the the program's attributes
  generating and caching compatible variants internally.
* A :py:class:`~arcade.gl.Query` class was added for easy access to low level
  measuring of opengl rendering calls. We can get the number samples written,
  number of primitives processed and time elapsed in nanoseconds.
* Added support for the buffer protocol. When ``arcade.gl`` requires byte data
  we can also pass objects like numpy array of pythons ``array.array`` directly
  not having to convert this data to bytes.

Version 2.4 New Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* New Tutorial: :ref:`pymunk_platformer_tutorial`
* New Tutorial: :ref:`view-tutorial`
* New Tutorial: :ref:`solitaire_tutorial`
* New Tutorial: :ref:`gpu_particle_burst`
* Several new and updated examples on :ref:`example-code`
* `New performance testing project <https://craven-performance-testing.s3-us-west-2.amazonaws.com/index.html>`_
* A lot of improvements to https://learn.arcade.academy
* `Instructional videos <https://www.youtube.com/playlist?list=PLUjR0nhln8uaI277eQfKkM8Nhp-xARriu>`_
  added to for https://learn.arcade.academy

Version 2.4 'Experimental'
~~~~~~~~~~~~~~~~~~~~~~~~~~

There is now an ``arcade.experimental`` module that holds code still under
development. Any code in this module might still have API changes.

Special Thanks
~~~~~~~~~~~~~~

Special thanks to `Einar Forselv <https://github.com/einarf>`_ and
`Maic Siemering <https://github.com/eruvanos>`_ for their significant work in helping
put this release together.

Version 2.3.15
--------------

*Release Date: Apr-14-2020*

* Bug Fix: Fix invalid empty text width `Issue 633 <https://github.com/pvcraven/arcade/issues/633>`_
* Bug Fix: Make sure file name is string before checking resources `Issue 636 <https://github.com/pvcraven/arcade/issues/636>`_
* Enhancement: Implement Size and Rotation for Tiled Objects `Issue 638 <https://github.com/pvcraven/arcade/issues/638>`_
* Documentation: Fix incorrect link to 'sprites following player' example

Version 2.3.14
--------------

*Release Date: Apr-9-2020*

* Bug Fix: Another attempt at fixing sprites with different dimensions added to
  same SpriteList didn't display correctly `Issue 630 <https://github.com/pvcraven/arcade/issues/630>`_
* Add lots of unit tests around Sprites and texture loading.

Version 2.3.13
--------------

*Release Date: Apr-8-2020*

* Bug Fix: Sprites with different dimensions added to same SpriteList didn't display correctly `Issue 630 <https://github.com/pvcraven/arcade/issues/630>`_

Version 2.3.12
--------------

*Release Date: Apr-8-2020*

* Enhancement: Support more textures in a SpriteList `Issue 332 <https://github.com/pvcraven/arcade/issues/332>`_

Version 2.3.11
--------------

*Release Date: Apr-5-2020*

* Bug Fix: Fix procedural_caves_bsp.py
* Bug Fix: Improve Windows install docs `Issue 623 <https://github.com/pvcraven/arcade/issues/623>`_


Version 2.3.10
--------------

*Release Date: Mar-31-2020*

* Bug Fix: Remove unused AudioStream and PlaysoundException from __init__
* Remove attempts to load ffmpeg library
* Add background music example
* Bug Fix: Improve Windows install docs `Issue 619 <https://github.com/pvcraven/arcade/issues/619>`_
* Add tutorial on edge artifacts `Issue 418 <https://github.com/pvcraven/arcade/issues/418>`_
* Bug Fix: Can't remove sprite from multiple lists `Issue 621 <https://github.com/pvcraven/arcade/issues/621>`_
* Several documentation updates

Version 2.3.9
-------------

*Release Date: Mar-25-2020*

* Bug Fix: Fix for calling SpriteList.remove `Issue 613 <https://github.com/pvcraven/arcade/issues/613>`_
* Bug Fix: get_image not working correctly on hi-res macs `Issue 594 <https://github.com/pvcraven/arcade/issues/594>`_
* Bug Fix: Fix for "shiver" in simple physics engine `Issue 614 <https://github.com/pvcraven/arcade/issues/614>`_
* Bug Fix: Fix for create_line_strip `Issue 616 <https://github.com/pvcraven/arcade/issues/616>`_
* Bug Fix: Fix for volume control `Issue 610 <https://github.com/pvcraven/arcade/issues/610>`_
* Bug Fix: Fix for loading SoLoud under Win64 `Issue 615 <https://github.com/pvcraven/arcade/issues/615>`_
* Fix jumping/falling texture in platformer example
* Add tests for gui.theme `Issue 605 <https://github.com/pvcraven/arcade/issues/605>`_
* Fix bad link to arcade.color docs

Version 2.3.8
-------------

*Release Date: Mar-09-2020*

* Major enhancement to sound. Uses SoLoud cross-platform library. New features include
  support for sound volume, sound stop, and pan left/right.

Version 2.3.7
-------------

*Release Date: Feb-27-2020*

* Bug Fix: If setting color of sprite with 4 ints, also set alpha
* Enhancement: Add image for code page 437
* Bug Fix: Fixes around hit box calcs `Issue 601 <https://github.com/pvcraven/arcade/issues/601>`_
* Bug Fix: Fixes for animated tiles and loading animated tiles from tile maps `Issue 603 <https://github.com/pvcraven/arcade/issues/603>`_

Version 2.3.6
-------------

*Release Date: Feb-17-2020*

* Enhancement: Add texture transformations `Issue 596 <https://github.com/pvcraven/arcade/issues/596>`_
* Bug Fix: Fix off-by-one issue with default viewport
* Bug Fix: Arcs are drawn double-sized `Issue 598 <https://github.com/pvcraven/arcade/issues/598>`_
* Enhancement: Add ``get_sprites_at_exact_point`` function
* Enhancement: Add code page 437 to default resources

Version 2.3.5
-------------

*Release Date: Feb-12-2020*

* Bug Fix: Calling sprite.draw wasn't drawing the sprite if scale was 1 `Issue 575 <https://github.com/pvcraven/arcade/issues/575>`_
* Add unit test for Issue 575
* Bug Fix: Changing sprite scale didn't cause sprite to redraw in new scale `Issue 588 <https://github.com/pvcraven/arcade/issues/588>`_
* Add unit test for Issue 588
* Enhancement: Simplify using built-in resources `Issue 576 <https://github.com/pvcraven/arcade/issues/576>`_
* Fix for failure on on_resize(), which pyglet was quietly ignoring
* Update ``rotate_point`` function to make it more obvious it takes degrees


Version 2.3.4
-------------

*Release Date: Feb-08-2020*

* Bug Fix: Sprites weren't appearing `Issue 585 <https://github.com/pvcraven/arcade/issues/585>`_


Version 2.3.3
-------------

*Release Date: Feb-08-2020*

* Bug Fix: set_scale checks height rather than scale `Issue 578 <https://github.com/pvcraven/arcade/issues/578>`_
* Bug Fix: Window flickers for drawing when not derived from Window class `Issue 579 <https://github.com/pvcraven/arcade/issues/579>`_
* Enhancement: Allow joystick selection in dual-stick shooter `Issue 571 <https://github.com/pvcraven/arcade/issues/571>`_
* Test coverage reporting now working correctly with TravisCI
* Improved test coverage
* Improved documentation and typing with Texture class
* Improve minimal View example

Version 2.3.2
-------------

*Release Date: Feb-01-2020*

* Remove scale as a parameter to load_textures because it is not unused
* Improve documentation
* Add example for acceleration/friction

Version 2.3.1
-------------

*Release Date: Jan-30-2020*

* Don't auto-update sprite hit box with animated sprite
* Fix issues with sprite.draw
* Improve error message given when trying to do a collision check and there's no
  hit box set on the sprite.

Version 2.3.0
-------------

*Release Date: Jan-30-2020*

* Backwards Incompatability: arcade.Texture no longer has a scale property. This
  property made things confusing as Sprites had their own scale attribute. This
  seemingly small change required a lot of rework around sprites, sprite lists,
  hit boxes, and drawing of textured rectangles.
* Include all the things that were part of 2.2.8, but hopefully working now.
* Bug Fix: Error when calling Sprite.draw() `Issue 570 <https://github.com/pvcraven/arcade/issues/570>`_
* Enhancement: Added Sprite.draw_hit_box to visually draw the hit box. (Kind of slow, but useful for debugging.)

Version 2.2.9
-------------

*Release Date: Jan-28-2020*

* Roll back to 2.2.7 because bug fixes in 2.2.8 messed up scaling

Version 2.2.8
-------------

*Release Date: Jan-27-2020*

* Version number now contained in one file, rather than three.
* Enhancement: Move several GitHub-listed enhancements to the .rst enhancement list
* Bug Fix: Texture scale not accounted for when getting height `Issue 516 <https://github.com/pvcraven/arcade/issues/516>`_
* Bug Fix: Issue with text cut off if it goes below baseline `Issue 515 <https://github.com/pvcraven/arcade/issues/515>`_
* Enhancement: Allow non-cached texture creation, fixing issue with resizing `Issue 506 <https://github.com/pvcraven/arcade/issues/506>`_
* Enhancement: Physics engine supports rotation
* Bug Fix: Need to better resolve collisions so sprite doesn't get hyper-spaces to new weird spot `Issue 569 <https://github.com/pvcraven/arcade/issues/569>`_
* Bug Fix: Hit box not getting properly created when working with multi-texture player sprite. `Issue 568 <https://github.com/pvcraven/arcade/issues/568>`_
* Bug Fix: Issue with text_sprite and anchor y of top `Issue 567 <https://github.com/pvcraven/arcade/issues/567>`_
* Bug Fix: Issues with documentation

Version 2.2.7
-------------

*Release Date: Jan-25-2020*

* Enhancement: Have draw_text return a sprite `Issue 565 <https://github.com/pvcraven/arcade/issues/565>`_
* Enhancement: Improve speed when changing alpha of text `Issue 563 <https://github.com/pvcraven/arcade/issues/563>`_
* Enhancement: Add dual-stick shooter example `Issue 301 <https://github.com/pvcraven/arcade/issues/301>`_
* Bug Fix: Fix for Pyglet 2.0dev incompatability `Issue 560 <https://github.com/pvcraven/arcade/issues/560>`_
* Bug Fix: Fix broken particle_systems.py example `Issue 558 <https://github.com/pvcraven/arcade/issues/558>`_
* Enhancement: Added mypy check to TravisCI build `Issue 557 <https://github.com/pvcraven/arcade/issues/557>`_
* Enhancement: Fix typing issues `Issue 537 <https://github.com/pvcraven/arcade/issues/537>`_
* Enhancement: Optimize load font in draw_text `Issue 525 <https://github.com/pvcraven/arcade/issues/525>`_
* Enhancement: Reorganize examples
* Bug Fix: get_pixel not working on MacOS `Issue 539 <https://github.com/pvcraven/arcade/issues/539>`_


Version 2.2.6
-------------

*Release Date: Jan-20-2020*

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
* Enhancement: Close enhancement-related github issues and reference them in the new enhancement list.

Version 2.2.5
-------------

*Release Date: Jan-17-2020*

* Enhancement: Improved speed when rendering non-buffered drawing primitives
* Bug fix: Angle working in radians instead of degrees in 2.2.4 `Issue 552 <https://github.com/pvcraven/arcade/issues/552>`_
* Bug fix: Angle and color of sprite not updating in 2.2.4 `Issue 553 <https://github.com/pvcraven/arcade/issues/553>`_


Version 2.2.4
-------------

*Release Date: Jan-15-2020*

* Enhancement: Moving sprites now 20% more efficient.

Version 2.2.3
-------------

*Release Date: Jan-12-2020*

* Bug fix: Hit boxes not getting updated with rotation and scaling. `Issue 548 <https://github.com/pvcraven/arcade/issues/548>`_
  This update depricates Sprite.points and instead uses Sprint.hit_box and Sprint.get_adjusted_hit_box
* Major internal change around not having ``__init__`` do ``import *`` but
  specifically name everything. `Issue 537 <https://github.com/pvcraven/arcade/issues/537>`_
  This rearranded a lot of files and also reworked the quickindex in documentation.


Version 2.2.2
-------------

*Release Date: Jan-09-2020*

* Bug fix: Arcade assumes tiles in tileset are same sized `Issue 550 <https://github.com/pvcraven/arcade/issues/550>`_

Version 2.2.1
-------------

*Release Date: Dec-22-2019*

* Bug fix: Resource folder not included in distribution `Issue 541 <https://github.com/pvcraven/arcade/issues/541>`_

Version 2.2.0
-------------

*Release Date: Dec-19-2019**

* Major Enhancement: Add built-in resources support `Issue 209 <https://github.com/pvcraven/arcade/issues/209>`_
  This also required many changes to the code samples, but they can be run now without
  downloading separate images.
* Major Enhancement: Auto-calculate hit box points by trimming out the transparency
* Major Enhancement: Sprite sheet support for the tiled map editor works now
* Enhancement: Added ``load_spritesheet`` for loading images from a sprite sheet
* Enhancement: Updates to physics engine to better handle non-rectangular sprites
* Enhancement: Add SpriteSolidColor class, for creating a single-color rectangular sprite
* Enhancement: Expose type hints to modules that depend on Arcade via PEP 561
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

* Fix: Error when importing Arcade on Raspberry Pi 4  `Issue 485 <https://github.com/pvcraven/arcade/issues/485>`_
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
* Add new view switching framework http://arcade.academy/example_code/how_to_examples/index.html#view-management
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
