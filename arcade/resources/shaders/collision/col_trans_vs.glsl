#version 330
// A simple passthrough shader forwarding data to the geomtry shader

in vec2 in_pos;
in vec2 in_size;
out vec2 v_pos;
out vec2 v_size;

void main() {
    v_pos = in_pos;
    v_size = in_size;
}
