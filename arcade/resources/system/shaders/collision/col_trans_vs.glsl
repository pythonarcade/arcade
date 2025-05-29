#version 330
// Buffer version if collision shader

in vec4 in_pos;
in vec2 in_size;

out vec2 pos;
out vec2 size;

void main() {
    pos = in_pos.xy;
    size = in_size;
}
