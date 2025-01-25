Camera
======

This is a rough overview of how the Cameras work. Updating and improving this documentation is on the roadmap.

Key Concepts
------------

World Space
^^^^^^^^^^^
Whenever an object has a position within Arcade that position is in world space. How much 1 unit in world
space represents is arbitrary. For example when a sprite has a scale of 1.0 then 1 unit in world space is
equal to one pixel of the sprite's source texture. This does not necessarily equate to one pixel on the screen.

Screen Space
^^^^^^^^^^^^
The final positions of anything drawn to screen is in screen space. The mouse positions returned by window
events like :py:func:`on_mouse_press` are also in screen space. Moving 1 unit in screen space is equivalent to moving
one pixel. Often positions in screen space are integer values, but this is not a strict rule.

View Matrices
^^^^^^^^^^^^^
The view matrix represents what part of world space should be focused on. It is made of three components.
The first is the position. This represents what world space position should be at (0, 0, 0). The second is
the forward vector. This is the direction which is considered forward and backwards in world space. the 
final component is the up vector. Which determines what world space positions are upwards or downwards in
world space.

The goal of the view matrix is to prepare everything in world space for projection into screen space. It
achieves this by applying its three components to every world space position. In the end any object with
a world space position equal to the view matrix position will be at (0, 0, 0). Any object along the forward
vector after moving will be placed along the z-axis, and any object along the up vector will be place along
the y-axis. This transformation moves the objects from screen space into view space. Importantly one unit in
world space is equal to one unit in view space

Projection Matrices
^^^^^^^^^^^^^^^^^^^
The projection matrix takes the positions of objects in view space and projects them into screen space. 
depending on the type of projection matrix how this exactly applies changes. Projection matrices alone
do not fully project objects into screen space, instead they transform positions into unit space. This 
special coordinate space ranges from -1 to 1 in the x, y, and z axis. Anything within this range will
be transformed into screen space, and everything outside this range is discarded and left undrawn.
you can conceptualise projection matrices as taking a 6 sided 3D volume in view space and 
squashing it down into a uniformly sized cube. In every case the closest position projected along the
z-axis is given by the near value, while the furthest is given by the far value.

orthographic
""""""""""""
In an orthographic projection the distance from the origin does not impact how much a position gets projected.
This type of projection can be visualised as a rectangular prism with a set width, height, and depth 
determined by left, right, bottom, top, near, far values. These values tell you the bounding box of positions
in view space which get projected.

perspective
"""""""""""
In an orthographic projection the distance from the origin directly impacts how much a position is projected.
This type of projection can be visualised as a rectangular prism with the sharp end removed. This shape means
that more positions further away from the origin will be squashed down into unit space. This makes objects 
that are further away appear smaller. The shape of the prism is determined by an aspect ratio, the field of view,
and the near and far values. The aspect ratio defines the ratio between the height and width of the projection. 
The field of view is half of the angle used to determine the height of the projection at a particular depth.

Viewports
^^^^^^^^^
The final concept to cover is the viewport. This is the pixel area which the unit space will scale to. The ratio
between the size of the viewport and the size of the projection determines the relationship between units in 
world space and pixels in screen space. For example if width and height of an orthographic projection is equal
to the width and height of the viewport then one unit in world space will equal one pixel in screen space. This
is the default for arcade.

The viewport also defines which pixels get drawn to in the final image. Generally this is equal to the entire 
screen, but it is possible to draw to only a specific area by defining the right viewport. Note that doing this
will change the ratio of the viewport and projection, so ensure that they match if you would like to keep the same
unit to pixel ratio. Any position outside the viewport which would normally be a valid pixel position will 
not be drawn.

Key Objects
-----------

- Objects which modify the view and perspective matrices are called "Projectors"

  - :py:class:`arcade.camera.Projector` is a :py:class:`Protocol` used internally by arcade
  - :py:func:`Projector.use()` sets the internal projection and view matrices used by Arcade and Pyglet
  - :py:func:`Projector.activate()` is the same as use, but works within a context manager using the ``with`` syntax
  - :py:func:`Projector.unproject(screen_coordinate)` provides a way to find the world position of any pixel position on screen.
  - :py:func:`Projector.project(world_coordinate)` provides a way to find the screen position of any position in the world.

- There are multiple data types which provide the information required to make view and projection matrices

  - :py:class:`camera.CameraData` holds the position, forward, and up vectors along with a zoom value used to create the view matrix
  - :py:class:`camera.OrthographicProjectionData` holds the left, right, bottom, top, near, far values needed to create a orthographic projection matrix
  - :py:class:`camera.PerspectiveProjectionData` holds the aspect ratio, field of view, near and far needed to create a perspective projection matrix.

- There are three primary `Projectors` in `arcade.camera`

  - :py:class:`arcade.camera.Camera2D` is locked to the x-y plane and is perfect for most use cases within arcade.
  - :py:class:`arcade.camera.OrthographicProjector` can be freely positioned in 3D space, and the scale of objects does not depend on the distance from the projector.
  - :py:class:`arcade.camera.PerspectiveProjector` can be freely positioned in 3D space, and objects look smaller the further from the camera they are.
