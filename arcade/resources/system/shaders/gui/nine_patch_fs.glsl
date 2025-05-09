#version 330

uniform sampler2D sprite_texture;
out vec4 fragColor;

in vec2 uv;

void main() {
   fragColor = texture(sprite_texture, uv);
}
