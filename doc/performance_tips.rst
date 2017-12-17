Performance Tips
================

Get the location of a sprite faster
-----------------------------------

When setting and getting the position of a ``Sprite`` class, use ``mysprite.position[0]``
for ``center_x`` and ``mysprite.position[1]`` for ``center_y``. Avoid using
the left/right/top/bottom attributes.

Do not mix moving and non-moving sprites in the same list when drawing. If any
sprite moves, the entire list of points has to be sent to the graphics card again.