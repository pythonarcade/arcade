#version 330

// (x, y) position passed in
in vec2 in_pos;

// Output the color to the fragment shader
out vec4 color;

void main() {

    // Set the RGBA color
    color = vec4(1, 1, 1, 1);

    // Set the position. (x, y, z, w)
    gl_Position = vec4(in_pos, 0.0, 1);
}