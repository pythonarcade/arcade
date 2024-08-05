
# Change Log

You can grab pre-release versions from PyPi. See the available versions from the
Arcade [PyPi Release History](https://pypi.org/project/arcade/#history) page.

## Version 3.0.0

Version 3.0.0 is a major update to Arcade. It is not 100% compatible with the 2.6 API.

### Breaking Changes

These are the API changes which could require updates to existing code based on
the 2.6 API. Some of these things may be repeated in the "Updates" section of
these release notes, however we have compiled the breaking changes here for an
easy reference. There may be other behavior changes that could break specific
scenarios, but this section is limited to changes which directly changed the
API in a way that is not compatible with how it was used in 2.6.

* `Sprite.angle` has changed to clockwise. So everything rotates different now.
* `Sprite.on_update` has been removed. Use `Sprite.update` instead. This now
  also has a `delta_time` parameter and accept/forwards `*args` and `**kwargs`
  to support custom parameters. The same applies to `SpriteList`.
* Signature for Sprite creation has changed.
* The deprecated `update()` function has been removed from the
  `arcade.Window`, `arcade.View`,
  `arcade.Section`, and `arcade.SectionManager` classes.
  Instead, please use the `arcade.Window.on_update()` function.
  It works the same as the `update` function, but has a ``delta_time``
  parameter which holds the time in seconds since the last update.
* The `update_rate` parameter of `arcade.Window` can no longer be set to `None`.
  Previously it defaulted to `1 / 60` however could be set to `None`. The default
  is still the same, but setting it to None will not do anything.
* Sprites created from the `~arcade.tilemap.TileMap` class would previously set a
  key in the `Sprite.properties` dictionary named `type`. This key has been renamed
  to ``class``. This is in keeping with Tiled's renaming of the key and following
  the Tiled format/API as closely as possible.
* The `arcade.text_pillow` and `arcade.text_pyglet` modules have been completely
  removed. The Pillow implementation is gone, and the Pyglet one has been renamed
  to just `arcade.text`. These modules were largely internal, but it is possible
  to have referenced them directly.
* Due to the above change and removal of the Pillow text implementation, the
  `arcade.create_text_sprite` previously referred to the Pillow text implementation,
  and there was no easy way to create a sprite from Text with the pyglet implementation.
  This function has been re-worked to use the pyglet based text system. It has no
  API breaking changes, but the underlying functionality has changed a lot, so if
  you are using this function it may be worth checking the docs for it again. The
  main concern for a difference here would be if you are also using any custom
  `arcade.TextureAtlas`.
* The GUI package has been changed significantly.
* Buffered shapes (shape list items) have been moved to their own sub-module.
* `use_spatial_hash` parameter for `SpriteList` and `TileMap` is now a `bool` instead
  of `Optional[bool]`
* `arcade.draw_text()` and `arcade.text.Text` arguments have changed. The `start_x`
  and `start_y` parameters have been removed. The `x` and `y` parameters are now
  required. `align!=left` does not interfere with `multiline` parameter anymore.
* GUI
  * Removed `arcade.gui.widgets.UIWrapper` this is now general available in `arcade.gui.widgets.UILayout`
  * Removed `arcade.gui.widgets.UIBorder` this is now general available in `arcade.gui.widgets.UIWidget`
  * Removed `arcade.gui.widgets.UIPadding` this is now general available in `arcade.gui.widgets.UIWidget`
  * Removed `arcade.gui.widgets.UITexturePane` this is now general available in `arcade.gui.widgets.UIWidget`
  * Removed `arcade.gui.widgets.UIAnchorWidget` replaced by `arcade.gui.widgets.UIAnchorLayout`

### Featured Updates

* Arcade now supports mixing Pyglet and Arcade drawing . This means
  you can, for example, use Pyglet batches. Pyglet batches can draw thousands
  of Pyglet objects with the cost and performance time of only a few.
* The code behind the texture atlas Arcade creates for each SpriteList  has
  been reworked to be faster and more efficient. Reversed/flipped sprites are
  no longer duplicated.
* Arcade now supports OpenGL ES 3.1/3.2 and have been
  tested on the Raspberry Pi 4 and 5. Any model using the Cortex-A72
  or Cortex-A76 CPU should work. Use images from 2024 or later for best
  results.
* Alpha blending (handling of transparency) is no longer globally enabled.
  This is now enabled by the objects and functions doing the drawing.
  Additional arguments have been added to draw functions and/or objects like
  `SpriteList` and `ShapeElementList` to toggle blending states. Blending
  states will always be reset after drawing.

### Changes

* `arcade.Window`
  * Removal of the `update` function in favor of `arcade.Window.on_update()`
  * `update_rate` parameter in the constructor can no longer be set to `None`.
    Must be a float.
  * Added `draw_rate` parameter to constructor
    `arcade.Window.__init__`, this will control the interval that the
    `arcade.Window.on_draw()` function is called at. This can be used
    with the pre-existing `update_rate` parameter which controls
    `arcade.Window.on_update()` to achieve separate draw and update rates.
  * `open_window()` now accepts `**kwargs` to pass additional parameters to the
    `arcade.Window` constructor.

* `arcade.View`
  * Removal of the ``update`` function in favor of `arcade.View.on_update()`

* `arcade.Section` and `arcade.SectionManager`

  * Removal of the ``update`` function in favor of `arcade.Section.on_update()`

* GUI

  * `arcade.gui.widgets.UIWidget`

    * Supports padding, border and background (color and texture)
    * Visibility: visible=False will prevent rendering of the widget. It will also
      not receive any UI events
    * Dropped `arcade.gui.widget.UIWidget.with_space_around()`
    * ``UIWidget.with_`` methods do not wrap the widget anymore, they only change
      the attributes
    * Fixed an blending issue when rendering the gui surface to the screen
    * Support nine patch information to draw background texture
    * Performance improvements
    * Removed some attributes from public interface, use `UIWidget.with_` methods
      * `UIWidget.border_width`
      * `UIWidget.border_color`
      * `UIWidget.bg_color`
      * `UIWidget.bg_texture`
      * `UIWidget.padding_top`
      * `UIWidget.padding_right`
      * `UIWidget.padding_bottom`
      * `UIWidget.padding_left`
    * Update and add example code.
    * Iterable (providing direct children)

  * New widgets:

    * `arcade.gui.widgets.dropdown.UIDropdown`
    * `arcade.gui.widgets.image.UIImage`
    * `arcade.gui.widgets.slider.UISlider`
    * `arcade.gui.widgets.constructs.UIButtonRow`
      ([PR1580](https://github.com/pythonarcade/arcade/pull/1580))

  * `arcade.gui.UIInteractiveWidget` only reacts to left mouse button events

  * Arcade `arcade.gui.property.Property`:

    * Properties are observable attributes (supported: primitive, list and dict).
      Listener can be bound with `arcade.gui.property.bind`

  * All `arcade.gui.UILayout`s support `size_hint`, `size_hint_min`, `size_hint_max`.

    * `arcade.gui.UIBoxLayout`
    * `arcade.gui.UIAnchorLayout`
    * `arcade.gui.UIGridLayout` [PR1478](https://github.com/pythonarcade/arcade/pull/1478)

  * Replaces deprecated usage of `arcade.draw_text`

  * Misc Changes

    * `arcade.color_from_hex_string` changed to follow the CSS hex string standard
    * Windows Text glyph are now created with DirectWrite instead of GDI
    * Removal of various deprecated functions and parameters
    * OpenGL examples moved to
      `examples/gl <https://github.com/pythonarcade/arcade/tree/development/arcade/examples/gl>`_
      from ``experiments/examples``

* Sprites
  * The method signature for `arcade.Sprite.__init__` has been changed.
    (May break old code.)
  * The sprite code has been cleaned up and broken into parts.
  * `arcade.Sprite.angle` now rotates clockwise. Why it ever rotated
    the other way, and why it lasted so long, we do not know.

* Controller Input

  * Previously controllers were usable via the `arcade.joysticks` module. This
    module is still available in 3.0.
    However, it should largely be seen as deprecated for most people who want
    basic controller support. This module existed basically just as an alias to
    the Pyglet joysticks module. We now have a new `arcade.controller` module,
    which is similarly just an alias to Pyglet's newer
    Controller API. This change should make a much wider selection of controllers
    able to work with Arcade, and provide newer functionality and be
    easier to use for most cases than the joystick module. The joystick module
    may still be useful if you need specialty controllers such as racing
    wheels or flight sticks. All existing example code has been updated to use
    the new controller API.

* Text

  * Complete removal of the old PIL based text system. In Arcade 2.6 we had largely
    switched to the newer Pyglet based system, however there were still remnants of
    the PIL implementation around. Namely the `arcade.create_text_sprite` function
    which has been updated to use the Pyglet system. There's no API breaking change
    here but if you are using the function it would be worth reading the new docs
    for it, as there are some different considerations surrounding use of a custom
    `arcade.TextureAtlas` if you are also doing that. This function should now be
    much much faster than the old PIL implementation. The texture generation happens
    almost entirely on the GPU now.
  * As part of this move, the `arcade.text_pillow` module has been removed completely,
    and the `arcade.text_pyglet` module has been re-named just be `arcade.text`.
  * `arcade.draw_text` and `arcade.Text` both now accept a `start_z` parameter.
    This will allow advanced usage to set the Z position of the underlying Label.
    This parameter defaults to 0 and does not change any existing usage.

* `arcade.draw_commands`:

  * Added `arcade.draw_commands.draw_lbwh_rectangle_textured`

    * Replaces the now-deprecated `arcade.draw_commands.draw_lrwh_rectangle_textured`
    * Usage is exactly the same

* OpenGL

  * Support for OpenGL ES 3.1 and 3.2. 3.2 is fully supported, 3.1 is only supported
    if the `EXT_geometry_shader` extension is provided by the driver. This is part
    of the minimum spec in 3.2 so it is guaranteed to be there. This is the only
    optional extension that Arcade needs to function with 3.1.

    As an example, the Raspberry Pi 4/5 only supports OpenGL ES 3.1, however does
    provide this extension, so is fully compatible with Arcade.
  * Textures now support immutable storage for OpenGL ES compatibility.
  * Arcade is now using Pyglet's projection and view matrix.
    All functions setting matrices will update the Pyglet window's
    `view` and `projection` attributes. Arcade shaders is also using Pyglet's
    `WindowBlock` UBO.
  * Uniforms are now set using `glProgramUniform` instead of `glUniform` when the
    extension is available.
  * Fixed many implicit type conversions in the shader code for wider support.
  * Added `front_face` property on the context for configuring front face winding
    order of triangles
  * Added `cull_face` property on the context for configuring what triangle face to cull
  * Added support for bindless textures
  * Added support for 64 bit integer uniforms
  * Added support for 64 float uniforms

* `arcade.tilemap.TileMap`

  * Added support Tiles defined as a sub-rectangle of an image. See
    [Tiled 1.9 Release Notes](https://www.mapeditor.org/2022/06/25/tiled-1-9-released.html)
    for more information on this feature.
  * Changed the `Sprite.properties` key "type" to "class" to stay in line with Tiled's
    re-naming of this key in their API.
  * You can now define a custom texture atlas for SpriteLists created in a TileMap.
    You can provide a map default to the `texture_atlas` parameter of the `arcade.tilemap.Tilemap`
    class or the `arcade.tilemap.load_tilemap` function. This will be used by default
    on all layers, however it can be overridden on a per-layer basis as defined by
    the new `texture_atlas` key in the `layer_options` dictionary. If no custom atlas
    is provided, then the global default atlas will be used (This is how it works
    pre-Arcade 3.0).
  * Fix for animated tiles from sprite sheets
  * DefaultTextureAtlas: Added `sync_texture_image` method to sync the texture in
    the atlas back into the internal pillow image in the `arcade.Texture`.
  * DefaultTextureAtlas: Added `get_texture_image` method to get pixel data of a
    texture in the atlas as a pillow image.

* Collision Detection

  * Collision detection is now even faster.
  * Remove Shapely for collision detection as 3.11 is faster without it.

* Shape list

  * Add in `arcade.create_triangles_strip_filled_with_colors`
  * Moved all buffered items that can be added to a shape list to `arcade.shape_list`

* Documentation

  * Example code page has been reorganized
  * [CONTRIBUTING.md](https://github.com/pythonarcade/arcade/blob/development/CONTRIBUTING.md) page has been updated
  * Improve `background_parallax` example

* Experimental
  * Started on a system for drawing large background textures with parallax scrolling.
    This is still experimental and may change in the future.
  * Started on an experimental event based input system for controllers
  * Started an experiment with vector based sprites

Special thanks to
[Einar Forselv](https://github.com/einarf),
[Darren Eberly](https://github.com/Cleptomania),
[pushfoo](https://github.com/pushfoo),
[Maic Siemering](https://github.com/eruvanos),
[Cleptomania](https://github.com/Cleptomania),
[Aspect1103](https://github.com/Aspect1103),
[Alejandro Casanovas](https://github.com/janscas),
[Ibrahim](https://github.com/Ibrahim2750mi),
[Andrew](https://github.com/cspotcode),
[Alexander](https://github.com/ccntrq),
[kosvitko](https://github.com/kosvitko),
and
[pvcraven](https://github.com/pvcraven)
for their contributions to this release. Also, thanks to everyone on the
[Pyglet](https://github.com/pyglet/pyglet) team! We depend heavily on Pyglet's continued development.
