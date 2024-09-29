#version 330

// Texture atlas
uniform sampler2D sprite_texture;
// Global color set on the sprite list
uniform vec4 spritelist_color;

in vec2 gs_uv;
in vec4 gs_color;

out vec4 f_color;

void main() {
    vec4 basecolor = texture(sprite_texture, gs_uv);
    basecolor *= gs_color * spritelist_color;
    // Alpha test
    if (basecolor.a == 0.0) {
        discard;
    }
    f_color = basecolor;
}
