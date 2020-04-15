#version 330

in vec2 in_vert;
in vec4 in_color;
out vec4 vs_color;

void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
    vs_color = in_color;
}
