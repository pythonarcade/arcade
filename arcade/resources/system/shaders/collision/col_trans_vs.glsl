#version 330
// A simple passthrough shader forwarding data to the geomtry shader

in vec3 in_pos;
in vec2 in_size;

out vec2 pos;
out vec2 size;

void main() {
    pos = in_pos.xy;
    size = in_size;
}
