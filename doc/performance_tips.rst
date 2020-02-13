.. _performance:

Arcade Performance Information
==============================

**Drawing primitive performance:** Drawing lines, rectangles, and circles can
be slow. If you are encountering this, you can speed things up by using
ShapeElement lists where you batch together the drawing commands.

**Sprite drawing performance:** If your sprites don't move, when creating the
sprite list set ``is_static`` to True. This allows Arcade to load the sprites to
the graphics card and just keep them there.

**Collision detection performance:** If it is taking too long to detect collisions
between sprites, make sure that the SpriteList with all the sprites has
``use_spatial_hasing`` turned on.