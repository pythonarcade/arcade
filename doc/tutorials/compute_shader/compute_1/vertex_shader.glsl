#version 330

in vec4 in_vert;
in vec4 in_col;

out vec2 v_pos;
out float v_radius;
out vec4 v_col;

void main()
{
    v_pos = in_vert.xy;
    v_radius = in_vert.w;
    v_col = in_col;
}