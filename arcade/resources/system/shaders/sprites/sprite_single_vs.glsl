#version 330
// Rendering a simple sprite or texture from uniforms because
// we want to avoid having to allocate a buffer for each sprite

uniform vec3 pos;
uniform vec2 size;
uniform vec4 color;
uniform float angle;
uniform float texture_id;

out vec2 v_size;
out vec4 v_color;
out float v_angle;
out float v_texture;

void main()
{
    gl_Position = vec4(pos, 1.0);
    v_size = size;
    v_color = color;
    v_angle = angle;
    v_texture = texture_id;
}
