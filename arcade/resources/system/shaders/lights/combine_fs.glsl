#version 330

uniform sampler2D diffuse_buffer;
uniform sampler2D light_buffer;
uniform vec3 ambient;

in vec2 vs_uv;
out vec4 f_color;

void main() {
    vec3 diffuse = texture(diffuse_buffer, vs_uv).rgb;
    vec3 light = texture(light_buffer, vs_uv).rgb;
    f_color = vec4(diffuse * ambient / 255.0 + diffuse * light, 1.0);
}
