#version 330

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

in vec2 in_position;
in vec2 in_uv;
out vec2 uv;

void main() {
    gl_Position = window.projection * window.view * vec4(in_position, 0.0, 1.0);
    uv = in_uv;
}
