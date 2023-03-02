#version 330

in vec3 in_pos;
in vec2 in_size;
in float in_angle;

out vec2 v_pos;
out vec2 v_size;
out float v_angle;

void main() {
    v_size = in_size;
    v_angle = in_angle;
    gl_Position = vec4(in_pos, 1.0);
}
