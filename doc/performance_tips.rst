Performance Tips
================

Draw Faster
-----------

Do not mix moving and non-moving sprites in the same list when drawing. If any
sprite moves, the entire list of points has to be sent to the graphics card again.