#version 330

// Time since burst start
uniform float time;

// (x, y) position passed in
in vec2 in_pos;

// Velocity of particle
in vec2 in_vel;

// Output the color to the fragment shader
out vec4 color;

void main() {

    // Set the RGBA color
    color = vec4(1, 1, 1, 1);

    // Calculate a new position
    vec2 new_pos = in_pos + (time * in_vel);

    // Set the position. (x, y, z, w)
    gl_Position = vec4(new_pos, 0.0, 1);
}