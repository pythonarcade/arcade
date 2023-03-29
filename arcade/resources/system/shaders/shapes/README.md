# Line Shaders

## Unbuffered

Unbuffered lines have a single color even when drawing
multiple lines. `draw_line` and `draw_lines`.
This shader is simpler just taking a color as a uniform
in the fragment shader.

## Buffered

Buffered lines need color passed in as a vertex attribute
because we are concatenating several different line
draw calls with different color configurations.
