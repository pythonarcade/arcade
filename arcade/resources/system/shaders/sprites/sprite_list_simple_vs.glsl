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
uniform sampler2D texture_id_data;
uniform isampler2D index_data;

// How much half-pixel offset to apply to the UVs.
// 0.0 is no offset, 1.0 is half a pixel offset
uniform float uv_offset_bias;

// Instanced geometry (rectangle as triangle strip)
in vec2 in_pos;

// Output to frag shader
out vec2 v_uv;
out vec4 v_color;

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

    // Apply half pixel offset modified by bias.
    // What bias to set depends on the texture filtering mode.
    // Linear can have 1.0 bias while nearest should have 0.0 (unless scale is 1:1)
    // uvs (
    //     0.0, 0.0,
    //     1.0, 0.0,
    //     0.0, 1.0,
    //     1.0, 1.0
    // )
    vec2 hp = 0.5 / vec2(textureSize(sprite_texture, 0)) * uv_offset_bias;
    uv0 += hp;
    uv1 += vec2(-hp.x, hp.y);
    uv2 += vec2(hp.x, -hp.y);
    uv3 += -hp;

    int vertex_id = gl_VertexID % 4;
    vec2 uvs[4] = vec2[4](uv0, uv2, uv1, uv3);
    v_color = color;
    gl_Position = mvp * vec4(rot * (in_pos * size) + center.xy, 0.0, 1.0);
    v_uv = uvs[vertex_id];
}
