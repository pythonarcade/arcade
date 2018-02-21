Performance Tips
================

Get/set the location of a sprite faster
---------------------------------------

When setting and getting the position of a ``Sprite`` class, use:

* ``mysprite.position[0]`` instead of ``mysprite.center_x``
* ``mysprite.position[1]`` instead of ``mysprite.center_y``

Try to avoid using the other methods like left/right/top/bottom for getting and
setting the position.

Draw Faster
-----------

Do not mix moving and non-moving sprites in the same list when drawing. If any
sprite moves, the entire list of points has to be sent to the graphics card again.