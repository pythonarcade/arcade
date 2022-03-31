#version 330

uniform Projection {
    uniform mat4 matrix;
} proj;

in vec2 in_vert;
in vec4 in_color;
out vec4 v_color;

void main() {
    gl_Position = proj.matrix * vec4(in_vert, 0.0, 1.0);
    v_color = in_color;
}
