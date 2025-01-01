# Change Log

You can grab pre-release versions from PyPi. See the available versions from the
Arcade [PyPi Release History](https://pypi.org/project/arcade/#history) page.

## Version 3.0.0

Version 3.0.0 is a major update to Arcade. It breaks compatibility with the 2.6 API.

### Breaking Changes
These are the breaking API changes. Use this as a quick reference for updating 2.6 code. You can find more details in later sections. Lots of behavior has changed even if the interface hasn't. If you are porting old code, read through these logs thoroughly.

* Dropped Python 3.8 support completely.
* Texture management has completely changed in 3.0. In the past, we
 cached everything, which caused issues for larger
 projects that needed memory management. Functions like `Arcade.load_texture` no longer cache textures.
* Removed the poorly named `Window.set_viewport` and `set_viewport` methods.
 `Camera2D` has completely superseded their functionality.
* Fixed `ArcadeContext` assuming that the projection and view matrices were aligned to the xy-plane and Orthographic. It is now safe to use full 3D matrices with Arcade.
* The `Sprite` initializer has been simplified. It's no longer possible to
 slice or transform textures through parameters in the sprite initializer.
 Use the `Texture` class to manipulate the sprite's texture.
 It supports transforms like rotating, scaling, flipping, and slicing.
* `Sprite.angle` has changed to clockwise.
* `Sprite.on_update` has been removed. Use `Sprite.update` instead. It has a `delta_time` parameter and accepts both `*args` and `**kwargs`
 to support custom parameters. The same applies to `SpriteList`.
* `Sprite.draw` has been removed. Use either `arcade.draw.draw_sprite`
 or an `arcade.SpriteList`.
* Removed `Sprite.face_point` and `Sprite.collision_radius`.
* The deprecated `update()` function has been removed from the
  `arcade.Window`, `arcade.View`,
  `arcade.Section`, and `arcade.SectionManager` classes.
 Instead, please use the `arcade.Window.on_update()` function.
 It works the same as the `update` function but has a "delta_time"
 parameter, which holds the time in seconds since the last update.
* The `update_rate` parameter of `arcade.Window` can no longer be set to `None`. It previously defaulted to `1 / 60` but could be set to `None`. The default is still the same, but setting it to None will not do anything.
* Sprites created from the `~arcade.tilemap.TileMap` class would previously set a key in the `Sprite.properties` dictionary named `type`. This key has been renamed to "class " in keeping with Tiled renaming the key.
* The `arcade.text_pillow` and `arcade.text_pyglet` modules have been completely removed. The Pillow implementation is gone, and the Pyglet version has been renamed `arcade.text`.
* Due to the above change. `arcade.create_text_sprite` has been reworked to use the Pyglet-based text system. It has no API-breaking changes, but the underlying functionality has changed drastically. It may be worth rechecking the docs if you use this function. The main concern is if you are using a custom `arcade.TextureAtlas`.
* Buffered shapes (shape list items) have been moved to their sub-module.
* The `use_spatial_hash` parameter for `SpriteList` and `TileMap` is now a `bool` instead of `Optional[bool]`
* `arcade.draw_text()` and `arcade.text.Text` arguments have changed. `x` and `y ` have replaced `start_x` and `start_y`. `align` no longer interferes with `multiline`.
* Moved or removed items from `arcade.util`:
  * Removed:
    * `arcade.util.generate_uuid_from_kwargs`
    * `arcade.util._Vec2`:
      * This was an internal class as indicated by the `_` prefix
      * It was an old version of pyglet's `pyglet.math.Vec2`
      * Arcade code now uses `pyglet.math.Vec2` directly
  * Moved to `arcade.math`:
    * `arcade.util.rand_in_circle` is now:
      * located at `arcade.math.rand_in_circle`
      * better at returning an even distribution of points [PR2426](https://github.com/pythonarcade/arcade/pull/2426) (remove any `math.sqrt` wrapping it)
    * `arcade.util.rand_on_circle` is now `arcade.math.rand_on_circle`
    * `arcade.util.lerp` is now:
      * located at `arcade.math.lerp`
      * compatible with any type which implements numerical `+`, `-`, and `*` operators
        * NOTE: lerping vectors may be more efficient when using dedicated functions and methods:
            * When lerping `pylget.math.Vec2`, use one of:
              * `pyglet.math.Vec2`'s [built in `lerp` method](https://pyglet.readthedocs.io/en/development/modules/math.html#pyglet.math.Vec2.lerp)
              * `arcade.math.lerp_2d` for general `tuple` compatibility
            * When lerping `pylget.math.Vec3`, use one of:
              * `pyglet.math.Vec3`'s [built in `lerp` method](https://pyglet.readthedocs.io/en/development/modules/math.html#pyglet.math.Vec3.lerp)
              * `arcade.math.lerp_2d` for general `tuple` compatibility
    * `arcade.util.lerp_vec` is now `arcade.math.lerp_2d`
    * `arcade.util.rand_in_rect` is now `arcade.math.rand_in_rect`
    * `arcade.util.rand_on_line` is now `arcade.math.rand_on_line`
    * `arcade.util.rand_angle_360_deg` is now `arcade.math.rand_angle_360_deg`
    * `arcade.util.rand_angle_spread_deg` is now `arcade.math.rand_angle_spread_deg`
    * `arcade.util.rand_spread_deg` is now `arcade.math.rand_spread_deg`
    * `arcade.util.rand_magnitude` is now `arcade.math.rand_magnitude`

 
* GUI
  * Removed `arcade.gui.widgets.UIWrapper`. It is now a part of `arcade.gui.widgets.UILayout`.
  * Removed `arcade.gui.widgets.UIBorder`. It is now a part of `arcade.gui.widgets.UIWidget`.
  * Removed `arcade.gui.widgets.UIPadding`. It is now a part of `arcade.gui.widgets.UIWidget`.
  * Removed `arcade.gui.widgets.UITexturePane`. It is now a part of `arcade.gui.widgets.UIWidget`.
  * Removed `arcade.gui.widgets.UIAnchorWidget` has been replaced by `arcade.gui.widgets.UIAnchorLayout`.
* Resources
  * Removed unused resources from `resources/gui_basic_assets`.
    * `items/shield_gold.png`
    * `items/sword_gold.png`
    * `slider_thumb.png`
    * `slider_track.png`
    * `toggle/switch_green.png`
    * `toggle/switch_red.png`

### Featured Updates

* The texture atlas has been heavily reworked to be more efficient.

* Alpha blending (handling of transparency) is no longer globally enabled but instead enabled when needed. draw functions and objects like
  `SpriteList` and `ShapeElementList` have new arguments to toggle blending states. Blending states are now reset after drawing.
* Arcade now supports OpenGL ES 3.1/3.2 and has been
 tested on the Raspberry Pi 4 and 5. Any model using the Cortex-A72
 or Cortex-A76 CPU should work. Use images from 2024 or later for best
 results.
* Arcade now supports freely mixing Pyglet and Arcade code. You can now freely use Pyglet batches and Labels when preferred over Arcade's types. Note that texture/image handling is still a separate system.
* A fully functioning 2D camera allows for moving, rotating, and zooming and works with Arcade and Pyglet.
* Added a new `GLOBAL_CLOCK` and `GLOBAL_FIXED_CLOCK` accessable from `arcade.clock`. which provides global access to elapsed time, number of frames, and the last delta_time.

### Window and View

* Removed the `update` function in favor of `arcade.Window.on_update()`.
* The `update_rate` parameter in the constructor can no longer be set to `None` and must be a float.
* A new `draw_rate` parameter in `arcade.Window.__init__`, controls the call interval of `arcade.Window.on_draw(). It is now possible to separate the draw and update speeds of Arcade windows. Keeping `draw_rate` close to the refresh rate of the user's monitor while setting `update_rate` to a much shorter interval can greatly improve the perceived smoothness of your application.
* `open_window()` now accepts `**kwargs` to pass additional parameters to the `arcade.Window` constructor.
* `arcade.View`
  * Removal of the ``update`` function in favor of `arcade.View.on_update()`.
* `arcade.Section` and `arcade.SectionManager`
  * Removal of the ``update`` function in favor of `arcade.Section.on_update()`.
* Added a whole new `on_fixed_update` method, which is called with a regular delta time
  * Is also available for `arcade. View`.
  * Control the rate of fixed updates with the `fixed_rate`.
 parameter in `Window.__init__`.
  * Control the max number of fixed updates per regular update with the `fixed_rate_cap`
 parameter in `Window.__init__`.
 * See the updated event loop docs for an in-depth explanation of ``on_fixed_update`` vs. ``on_update``.

### Camera

* Created `arcade.camera.Camera2D`, which allows for easy manipulation of Arcade and Pyglet's rendering matrices.
* Created `arcade.camera.PerspectiveProjector` and `arcade.camera.OrthographicProjector`.
 Which can manipulate the matrices in 3D space.
* Created methods to rotate and move cameras.
* Created methods to generate view and projection matrices needed by projector objects.
* Created static projector classes to set the matrices with constant values.
* Added a default camera that automatically adjusts to the active render target.
* Added a camera shake object that makes adding a camera shake to a game easy.
* All `Projector` classes provide methods to project to and from the screen and world coordinates.

### Textures

* `arcade.load_texture` has been simplified to load the entire image. Use `arcade.load_spritesheet` to use better versions of the old arguments.
* `arcade.get_default_texture` and `arcade.get_default_image` are new methods to give `arcade.Sprite` their default texture.
* Added `sync_texture_image` to the `DefaultTextureAtlas` method to sync the texture in the atlas back into the internal pillow image in the `arcade.Texture`.
* DefaultTextureAtlas: Added `get_texture_image` method to get pixel data of a texture in the atlas as a pillow image.

### GUI

* `arcade.gui.widgets.UIWidget`
  * Supports padding, border, and background (color or texture).
  * Visibility: visible=False will prevent widget rendering. It will also
 not receive any UI events.
  * Dropped `arcade.gui.widget.UIWidget.with_space_around`.
  * `UIWidget.with_` methods no longer wrap the widget. They only change the attributes.
  * Fixed a blending issue when rendering the GUI surface to the screen.
  * Now supports nine-patch background textures.
  * General performance improvements.
  * Some attributes were removed from the public interface; use `UIWidget.with_` methods instead.
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

* Updated widgets
  * `arcade.gui.widgets.text.UIInputText` emits an `on_change` event.
  * `arcade.gui.widgets.slider.UITextureSlider` texture names changed to fit the naming pattern.

* New widgets:
  * `arcade.gui.widgets.dropdown.UIDropdown`
  * `arcade.gui.widgets.image.UIImage`
  * `arcade.gui.widgets.slider.UISlider`
  * `arcade.gui.widgets.constructs.UIButtonRow`
 ([PR1580](https://github.com/pythonarcade/arcade/pull/1580))

* `arcade.gui.UIInteractiveWidget` only reacts to left mouse button events.

* Arcade `arcade.gui.property.Property`:
  * Properties are observable attributes (supports primitive, list, and dict). A Listener can be bound with `arcade.gui.property.bind`.
* All `arcade.gui.UILayout`s now support `size_hint`, `size_hint_min`, and `size_hint_max`.
  * `arcade.gui.UIBoxLayout`
  * `arcade.gui.UIAnchorLayout`
  * `Arcade.gui.UIGridLayout` [PR1478](https://github.com/pythonarcade/arcade/pull/1478)

* Added color-consistent assets to `arcade.resources.gui_basic_assets`.
* Provide GUI-friendly color constants in `arcade.uicolor`.
* Replace deprecated usage of `arcade.draw_text`.

### Rect

* Added a `Rect` type, making working with axis-aligned rectangles easy.
  * Provides functions to create a full `Rect` object from four values.
  * Provides methods to move and scale the `Rect`.
  * Provides methods to compare against the `Rect` with 2D points and other `Rects`.
* Added `AnchorPoint` helpers and aliases for `Vec2`s in the range (0 - 1).
* Added several helper methods for creating `Rect` objects.
  * `LRBT(left, right, bottom, top)`
  * `LBWH(left, bottom, width, height)`
  * `XYWH(x, y, width, height, anchor = AnchorPoint.CENTER)`
  * `XYRR(center_x, center_y, half_width, half_height)` (this is mostly used for GL.)
  * `Viewport(left, bottom, width, height)` (where all inputs are `int`s.)
* Several properties in the library now return a `Rect`:
  * `Window.rect`
  * `BasicSprite.rect`
  * `OrthographicProjectionData.rect`
  * `UIWidget.rect`
  * `Section.rect`
* The drawing functions `draw_rect_filled()` and `draw_rect_outline()` can be used to draw a `Rect` directly.

### Misc Changes

* `arcade.experimental` has been split into two submodules, `experimental` and `future`.
  * `future` includes all incomplete features we intend to include in Arcade eventually
  * `experimental` is any interesting code that may not end up as Arcade features.
* `arcade.color_from_hex_string` changed to follow the CSS hex string standard.
* Made Pyglet's math classes accessible within Arcade.
* Arcade's utility math functions have more robust typing.
* Added `Point`, `Point2`, `Point3` type aliases for tuples and vectors.
* Added `Sequence` types for all three `Point` aliases.
* Added a `Color` object with a plethora of useful methods.
* Windows Text glyphs are now created with DirectWrite instead of GDI.
* Removal of various deprecated functions and parameters.
* OpenGL examples moved to _`examples/gl <https://github.com/pythonarcade/arcade/tree/development/arcade/examples/gl>`_
 from _"experiments/examples"_

### Sprites

* Created `BasicSprite`, the absolute minimum required for an Arcade sprite most users will do well sticking with `Sprite`.
* `Sprite.draw` has been completely removed. It was a wasteful and slow way to render a sprite. Use an `arcade.SpriteList` or `arcade.draw.draw_sprite`.
* `Sprite.visible` no longer overrides the sprite's alpha, allowing for toggling transparent sprites.
* `Sprite.face_towards` has been removed as it did not behave as expected and is not strictly for sprites.
* `Sprite.collision_radius` has been removed as it is no longer used in collision checking. Sprites now only rely on their hitbox.
* The `arcade.Sprite.__init__` has been changed to remove all references to texture loading. Use `arcade.load_texture` and `arcade.load_spritesheet` for more complex behavior.
* `arcade.Sprite.angle` now rotates clockwise following standard game behavior. It may break common linear algebra methods, but reversing the resulting angles is easy.

### Controller Input

Previously, controllers were usable via the `Arcade.joysticks` module. This module is still available in 3.0.
However, most people can treat it as depreciated. It is an alias to Pyglet's joysticks sub-module. There is now an `arcade.controller` module that is an alias to Pyglet's new Controller API. This change should make a more comprehensive choice of controllers usable with Arcade. The joystick module may still be helpful if you need specialty controllers such as racing wheels or flight sticks. The example code now uses the new controller AP.

### Text

* Complete removal of the old PIL-based text system. In 2.6, we switched to the newer Pyglet-based system, but there were still remnants of the PIL implementation—namely, the `arcade.create_text_sprite` function. There's no API breaking change, but if you are using the function, it would be worth reading the new docs, as there are some different considerations when using a custom `arcade.TextureAtlas`. This function is faster than the old PIL implementation. Texture generation happens almost entirely on the GPU now.
* The `arcade.text_pillow` module no longer exists.
* `arcade.text_pyglet` has been renamed `arcade.text`.
* `arcade.draw_text` and `arcade.Text` now accept a `z` parameter that defaults to 0. Previous text versions had the same default.

### `arcade.draw_*`

* `arcade.draw_commands` has been renamed `arcade.draw`.
* Added `arcade.draw.draw_lbwh_rectangle_textured` which replaces 
 the now-deprecated `arcade.draw_commands.draw_lrwh_rectangle_textured`. Usage has stayed the same as it was misnamed.

### OpenGL

* Support for OpenGL ES 3.1 and 3.2. 3.2 is fully supported, and 3.1 is only supported if the driver provides the `EXT_geometry_shader` extension. It is part of the minimum spec in 3.2, so it is guaranteed to be there. Arcade only needs this extension to function with 3.1.
 * For example, the Raspberry Pi 4/5 only supports OpenGL ES 3.1 but provides the extension, making it fully compatible with Arcade.
* Textures now support immutable storage for OpenGL ES compatibility.
* Arcade is now using Pyglet's projection and view matrix.
 All functions setting matrices will update the Pyglet window's
  `view` and `projection` attributes. Arcade shaders are also using Pyglet's `WindowBlock` UBO.
* Uniforms are now set using `glProgramUniform` instead of `glUniform` when the extension is available, improving performance.
* Fixed many implicit type conversions in the shader code for broader support.
* Added `front_face` property on the context for configuring the winding order of triangles.
* Added `cull_face` property to the context to configure what triangle faces to cull.
* Added support for bindless textures.
* Added support for 64-bit integer uniforms.
* Added support for 64-bit float uniforms.

### TileMap

* Now supports tiles defined as a sub-rectangle of an image. See [Tiled 1.9 Release Notes](https://www.mapeditor.org/2022/06/25/tiled-1-9-released.html) for more information on this feature.
* Changed the `Sprite.properties` key "type" to "class" to stay in line with Tiled's API.
* You can now define a custom texture atlas for SpriteLists created in a TileMap. You can provide a default with the `texture_atlas` parameter of the `arcade.tilemap.Tilemap` and `arcade.tilemap.load_tilemap`. The new `texture_atlas` key of the `layer_options` dict lets you control it per layer. The global `TextureAtlas` will be used by default (This is how it works pre-Arcade 3.0).
* Fixed animated tiles from sprite sheets.

### Collision Detection

* Collision detection is now even faster.
* Remove Shapely for collision detection, as Python 3.11+ is faster without it.

### Shape Lists

* New buffered `Arcade.create_triangles_strip_filled_with_colors`.
* `arcade.shape_list` now contains all items that can rendered using an `arcade.ShapeElementList`.

### Documentation

* Example code page has been reorganized.
* [CONTRIBUTING.md](https://github.com/pythonarcade/arcade/blob/development/CONTRIBUTING.md) has been updated.
* Improved `background_parallax` example.
* More detailed information on how Arcade's event loop works.
* The platformer tutorial has been overhauled.

### Future

* These features are all in active development, and their API can change anytime. Feedback is always appreciated.
* Started on a system for drawing large background textures with parallax scrolling. These don't use an `arcade.TextureAtlas` so they aren't batched, preventing your Atlas' from being filled with massive images.
* Started on an event-based input system, which includes improved Enums for key, mouse, and controller inputs. Using the InputManager, you can define custom actions that can rebound at run time and have multiple valid keys.
* Added a method to bootstrap `arcade.clock.Clock`, adding functionality to add sub-clocks that their parent will tick. This makes it much safer to manipulate the time of particular game objects.
* A new subclass of `arcade.BasicSprite` that used `pyglet.math.Vec2` for most of its properties. It has a heavy performance hit but is much nicer to work with.
* The experimental lighting features have been promoted to the future, but their implementation is very volatile. If you have ideas for what you'd like from a lighting module, please share them on Discord.

### Contributors

Contributing to a release comes in many forms. It can be code, documentation, testing, or providing feedback. It's hard to keep track of all the people involved in a release, but we want to thank everyone who has helped in any shape or form. We appreciate all of you!

#### The Arcade Team:

* [Andrew Bradley](https://github.com/cspotcode)
* [Alejandro Casanovas](https://github.com/janscas)
* [Cleptomania](https://github.com/Cleptomania)
* [DigiDuncan](https://github.com/DigiDuncan)
* [DragonMoffon](https://github.com/DragonMoffon)
* [Einar Forselv](https://github.com/einarf)
* [Maic Siemering](https://github.com/eruvanos)
* [pushfoo](https://github.com/pushfoo)
* [pvcraven](https://github.com/pvcraven)

We would also like to thank the contributors who spent their valuable time solving issues, squashing bugs, and writing documentation. We appreciate your help; you helped get 3.0 out the door!

#### Notable contributors:
* [DarkLight1337](https://github.com/DarkLight1337) helped the team untangle type annotation issues for cameras
* [Mohammad Ibrahim](https://github.com/Ibrahim2750mi) was a massive help with the GUI and various other parts of the library.
* [ryyst](https://github.com/ryyst) completely revitalized the Arcade Docs.

#### Contributors

* [Aizen](https://github.com/feiyuhuahuo)
* [Aurelio Lopez](https://github.com/Aurelioghs)
* [BrettskiPy](https://github.com/BrettskiPy)
* [Brian Stormont](https://github.com/MostTornBrain)
* [cacheguy](https://github.com/cacheguy)
* [Code Apprentice](https://github.com/codeguru42)
* [Dominik](https://github.com/NotYou404)
* [Ethan Chan](https://github.com/eschan147)
* [FriendlyGecko](https://github.com/FriendlyGecko)
* [Grant Hur](https://github.com/gran4)
* [Ian Currie](https://github.com/iansedano)
* [Jack Ashwell](https://github.com/JackAshwell11)
* [kosvitko](https://github.com/kosvitko)
* [L Cai](https://github.com/lbcai)
* [Miles Curry](https://github.com/MiCurry)
* [MrWardKKHS](https://github.com/MrWardKKHS)
* [Natalie Fearnley](https://github.com/nfearnley)
* [Omar Mohammed](https://github.com/osm3000)
* [Raccoon](https://github.com/bandit-masked)
* [Raxeli1](https://github.com/Rapen765)
* [Rémi Vanicat](https://github.com/vanicat)
* [Rich Saupe](https://github.com/sabadam32)
* [Shadow](https://github.com/shadow7412)
* [Shivani Arbat](https://github.com/shivaniarbat)
* [Snipy7374](https://github.com/Snipy7374)
* [Tiffany Xiao](https://github.com/tiffanyxiao)
* [Wilson (Fengchi) Wang](https://github.com/FengchiW)

Finally, thank you to the [Pyglet](https://github.com/pyglet/pyglet) team! Pyglet is the backbone of Arcade, and this library wouldn't be possible without them.

3.0.0 changes span from Mar 12, 2022 – <TBC>
