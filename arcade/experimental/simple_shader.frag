#version 330

uniform sampler2D tex;

in vec2 v_uv;
out vec4 f_color;

void main() {

    f_color = texture(tex, v_uv);
}