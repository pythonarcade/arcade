#version 330

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

uniform vec2 offset;

in vec2 in_vert;
in vec2 in_uv;

in vec2 in_instance_position;
in float in_instance_radius;
in float in_instance_attenuation;
in vec3 in_instance_color;

out float attenuation;
out vec3 color;
out vec2 uv;

void main() {
    vec2 position = (in_vert * in_instance_radius) + in_instance_position + offset;
    gl_Position = window.projection * window.view * vec4(position, 0.0, 1.0);
    uv = in_uv;
    attenuation = in_instance_attenuation;
    color = in_instance_color / 255.0;
}
