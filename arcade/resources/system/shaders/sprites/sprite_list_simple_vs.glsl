#version 330
// vert/frag only version of the sprite list shader

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

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

// Instanced geometry (rectangle as triangle strip)
in vec2 in_pos;

// Output to frag shader
out vec2 uv;
out vec4 color;

#include :system:shaders/lib/sprite.glsl

void main() {
    // Reading per-instance data from textures.
    // First we need take the index texture into account to get the correct rendering order.
    int index = getInstanceIndex(index_data, gl_InstanceID);
    vec4 pos_rot = getInstancePosRot(pos_data, index);
    vec2 size = getInstanceSize(size_data, index);  
    vec4 color = getInstanceColor(color_data, index);
    int texture_id = getInstanceTextureId(texture_id_data, index);
    // Read texture coordinates from UV texture here
    vec2 uv0, uv1, uv2, uv3;
    getSpriteUVs(uv_texture, texture_id, uv0, uv1, uv2, uv3);

    vec3 center = pos_rot.xyz;
    float angle = radians(pos_rot.w);
    mat2 rot = mat2(
        cos(angle), -sin(angle),
        sin(angle),  cos(angle)
    );

    mat4 mvp = window.projection * window.view;

    // TODO: Half pixel offset

    int vertex_id = gl_VertexID % 4;
    color = color;
    switch (vertex_id) {
        case 0:
            // Upper left
            gl_Position = mvp * vec4(rot * size + center.xy, center.z, 1.0);
            uv = uv0;
            break;
        case 1:
            // lower left
            gl_Position = mvp * vec4(rot * size + center.xy, center.z, 1.0);
            uv = uv2;
            break;
        case 2:
            // upper right
            gl_Position = mvp * vec4(rot * size + center.xy, center.z, 1.0);
            uv = uv1;
            break;
        case 3:
            // lower right
            gl_Position = mvp * vec4(rot * size + center.xy, center.z, 1.0);
            uv = uv3;
            break;
    }
}
