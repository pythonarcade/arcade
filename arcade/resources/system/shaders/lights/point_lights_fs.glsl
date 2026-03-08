#version 330

out vec4 f_color;

in vec2 uv;
in float attenuation;
in vec3 color;

void main() {
    // Distance to light 0.0 -> 1.0
    float dist = length(uv * 2.0 - vec2(1.0));

    // Skip fragments outside light
    if (dist > 1.0) discard;

    // Simple attenuation
    float att = (1.0 - dist + attenuation);
    f_color = vec4(color * clamp(att, 0.0, 1.0), 0.0);
}
