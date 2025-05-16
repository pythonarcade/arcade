#version 330

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

in vec3 in_pos;
in vec2 in_uv;

out vec2 uv;

void main() {
    gl_Position = window.projection * window.view * vec4(in_pos, 1.0);
    uv = in_uv;
}
