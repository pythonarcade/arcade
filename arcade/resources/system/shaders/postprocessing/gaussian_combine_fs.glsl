#version 330

uniform sampler2D color_buffer;
uniform sampler2D blur_buffer;

in vec2 v_uv;
out vec4 f_color;

void main() {
    f_color = texture(color_buffer, v_uv) + texture(blur_buffer, v_uv);
}
