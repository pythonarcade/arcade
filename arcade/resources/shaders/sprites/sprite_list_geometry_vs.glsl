#version 330

in vec2 in_pos;
in float in_angle;
in vec2 in_size;
in vec4 in_sub_tex_coords;
in vec4 in_color;

out float v_angle;
out vec4 v_color;
out vec2 v_size;
out vec4 v_sub_tex_coords;

void main() {
    gl_Position = vec4(in_pos, 0.0, 1.0);
    v_angle = in_angle;
    v_color = in_color;
    v_size = in_size;
    v_sub_tex_coords = in_sub_tex_coords;
}
