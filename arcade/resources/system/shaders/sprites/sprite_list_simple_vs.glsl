#version 330
// vert/frag only version of the sprite list shader

// Texture atlas
uniform sampler2D sprite_texture;
// Texture containing UVs for the entire atlas
uniform sampler2D uv_texture;

// Per instance data
uniform sampler2D pos_data;
uniform sampler2D size_data;
uniform sampler2D color_data;
uniform isampler2D texture_id_data;
uniform isampler2D index_data;

// How much half-pixel offset to apply to the UVs.
// 0.0 is no offset, 1.0 is half a pixel offset
uniform float uv_offset_bias;

// Per sprite/instance data
in vec3 in_instance_pos;
// Instanced geometry (rectangle as triangle strip)
in vec2 in_pos;

out vec2 uv;
out vec4 color;

#include :system:shaders/lib/sprite.glsl

void main() {
    // Read texture coordinates from UV texture here
    vec2 uv0, uv1, uv2, uv3;
    getSpriteUVs(uv_texture, int(in_instance_texture), uv0, uv1, uv2, uv3);

    // TODO: Half pixel offset
    // TODO: Position, rotation, size, color, uvs
}
