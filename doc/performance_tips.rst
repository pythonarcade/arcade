Performance Tips
================

Draw Faster
-----------

* Do not mix moving and non-moving sprites in the same list when drawing. If
  any sprite moves, the entire list of points has to be sent to the graphics
  card again.
* If you have a list of sprites that move, but you won't be checking for
  sprite collisions with that list, then don't use spatial hashing.
  When creating the list, set ``use_spatial_hash=False``.