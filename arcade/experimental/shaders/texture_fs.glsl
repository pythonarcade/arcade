#version 330

uniform sampler2D texture0;
uniform float time;

in vec2 v_uv;
out vec4 f_color;

void main() {
    f_color = texture(texture0, v_uv);
}
