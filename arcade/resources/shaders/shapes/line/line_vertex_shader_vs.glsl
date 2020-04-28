#version 330

uniform mat4 Projection;

in vec2 in_vert;
in vec4 in_color;
out vec4 v_color;

void main() {
    gl_Position = Projection * vec4(in_vert, 0.0, 1.0);
    v_color = in_color;
}
