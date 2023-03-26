#version 330

uniform sampler2D texture0;
uniform float contrast;
uniform float brightness;

in vec2 v_uv;
out vec4 f_color;

void main() {
    vec4 p = texture(texture0, v_uv);
    p.rgb *= contrast;
    // p.rgb += vec3(brightness);
    // simplified luma: 0.2, 0.7, 0.1
    float luma = p.r * 0.2 + p.g * 0.7 * p.b * 0.1;
    // if (luma < 0.5) discard;
    f_color = p * luma;
}
