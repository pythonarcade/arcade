#version 330

uniform mat4 Projection;

in vec2 in_vert;
in vec2 in_color;
out vec2 vs_color;

void main() {
    gl_Position = Projection * vec4(in_vert, 0.0, 1.0);
    vs_color = in_color;
}
