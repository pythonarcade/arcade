#version 330
// vert/frag only version of the sprite list shader

// Texture atlas
uniform sampler2D sprite_texture;
// Global color set on the sprite list
uniform vec4 spritelist_color;

in vec2 v_uv;
in vec4 v_color;

out vec4 f_color;

void main() {
    // vec4 base_color = v_color;
    vec4 base_color = texture(sprite_texture, v_uv);
    base_color *= v_color * spritelist_color;
    // Alpha test
    if (base_color.a == 0.0) {
        discard;
    }
    f_color = base_color;
}
