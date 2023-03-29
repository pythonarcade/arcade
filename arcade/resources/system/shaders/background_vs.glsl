#version 330

in vec2 in_vert;
in vec2 in_uv;

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

uniform vec2 size;
uniform vec2 pos;

out vec2 frag_uv;

void main() {
    frag_uv = in_uv;

    vec4 position = vec4(in_vert * size + pos, 0.0, 1.0);
    gl_Position = window.projection * window.view * position;
}
