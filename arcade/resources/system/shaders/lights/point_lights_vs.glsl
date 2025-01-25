#version 330

in vec2 in_vert;
in float in_radius;
in float in_attenuation;
in vec3 in_color;

out float vs_radius;
out float vs_attenuation;
out vec3 vs_color;

void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
    vs_radius = in_radius;
    vs_attenuation = in_attenuation;
    vs_color = in_color / 255.0;
}
