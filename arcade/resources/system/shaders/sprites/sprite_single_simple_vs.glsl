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

uniform vec4 pos_rot;  // rect.x, rect.y, 0, angle
uniform vec4 color;  // color.normalized
uniform vec2 size;  // rect.width, rect.height
uniform int texture_id;

// How much half-pixel offset to apply to the UVs.
// 0.0 is no offset, 1.0 is half a pixel offset
uniform float uv_offset_bias;

// Output to frag shader
out vec2 v_uv;
out vec4 v_color;

#include :system:shaders/lib/sprite.glsl


const vec2 vertices[4] = vec2[4](
    vec2(-0.5, +0.5),  // Upper left
    vec2(-0.5, -0.5),  // lower left
    vec2(+0.5, +0.5),  // upper right
    vec2(+0.5, -0.5)   // lower right
);

void main() {
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
    gl_Position = mvp * vec4(rot * (vertices[vertex_id] * size) + center.xy, 0.0, 1.0);
    v_uv = uvs[vertex_id];
}
