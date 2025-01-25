#version 330

uniform sampler2D sprite_texture;
out vec4 f_color;

in vec2 uv;

void main() {
   f_color = texture(sprite_texture, uv);
}
