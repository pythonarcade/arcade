#version 330
// Atlas resize without geometry shader

// The render target for this program is the new
// texture atlas texture

#include :system:shaders/lib/sprite.glsl

// Old and new texture coordinates
uniform sampler2D atlas_old;
uniform sampler2D atlas_new;

uniform sampler2D texcoords_old;
uniform sampler2D texcoords_new;

uniform mat4 projection;
uniform float border;

out vec2 uv;

void main() {
    // Get the texture sizes
    ivec2 size_old = textureSize(atlas_old, 0).xy;
    ivec2 size_new = textureSize(atlas_new, 0).xy;

    // Read texture coordinates from UV texture here
    int texture_id = gl_VertexID / 6;
    vec2 old_uv0, old_uv1, old_uv2, old_uv3;
    getSpriteUVs(texcoords_old, texture_id, old_uv0, old_uv1, old_uv2, old_uv3);
    vec2 new_uv0, new_uv1, new_uv2, new_uv3;
    getSpriteUVs(texcoords_new, texture_id, new_uv0, new_uv1, new_uv2, new_uv3);

    // Lower left corner flipped * size - border
    vec2 pos = vec2(new_uv2.x, 1.0 - new_uv2.y) * vec2(size_new) - vec2(border);
    // absolute value of the diagonal * size + border * 2
    vec2 size = abs(new_uv3 - new_uv0) * vec2(size_new) + vec2(border * 2.0);

    // We need to offset the old coordinates by border size
    vec2 pix_offset = vec2(border) / vec2(size_old);

    // Emit two triangles over 6 vertices
    switch (gl_VertexID % 6) {
        // First triangle
        case 0:
            // upper left
            uv = old_uv0 - pix_offset;
            gl_Position = projection * vec4(pos + vec2(0.0, size.y), 0.0, 1.0);
            break;
        case 1:
            // lower left   
            uv = old_uv2 + vec2(-pix_offset.x, pix_offset.y);
            gl_Position = projection * vec4(pos, 0.0, 1.0);
            break;
        case 2:
            // upper right
            uv = old_uv1 + vec2(pix_offset.x, -pix_offset.y);
            gl_Position = projection * vec4(pos + vec2(size.x, size.y), 0.0, 1.0);
            break;
        // Second triangle
        case 3:
            // lower left
            uv = old_uv2 + vec2(-pix_offset.x, pix_offset.y);
            gl_Position = projection * vec4(pos, 0.0, 1.0);
            break;
        case 4:
            // upper right
            uv = old_uv1 + vec2(pix_offset.x, -pix_offset.y);
            gl_Position = projection * vec4(pos + vec2(size.x, size.y), 0.0, 1.0);
            break;
        case 5:
            // lower right
            uv = old_uv3 + pix_offset;
            gl_Position = projection * vec4(pos + vec2(size.x, 0.0), 0.0, 1.0);
            break;
    }
}
