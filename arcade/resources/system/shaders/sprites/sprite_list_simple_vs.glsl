#version 330
// vert/frag only version of the sprite list shader

// Texture atlas
uniform sampler2D sprite_texture;
// Texture containing UVs for the entire atlas
uniform sampler2D uv_texture;
// How much half-pixel offset to apply to the UVs.
// 0.0 is no offset, 1.0 is half a pixel offset
uniform float uv_offset_bias;

in vec3 in_pos;
in float in_angle;
in vec2 in_size;
in float in_texture;
in vec4 in_color;
//

out vec2 uv;
out vec4 color;

#include :system:shaders/lib/sprite.glsl

void main() {
    // Read texture coordinates from UV texture here
    vec2 uv0, uv1, uv2, uv3;
    getSpriteUVs(uv_texture, int(in_texture), uv0, uv1, uv2, uv3);

    // TODO: Half pixel offset
    // TODO: Position, rotation, size, color, uvs

}
