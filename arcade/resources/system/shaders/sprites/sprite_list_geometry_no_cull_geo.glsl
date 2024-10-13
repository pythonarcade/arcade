#version 330

#include :system:shaders/lib/sprite.glsl

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

// Texture atlas
uniform sampler2D sprite_texture;
// Texture containing UVs for the entire atlas
uniform sampler2D uv_texture;
// How much half-pixel offset to apply to the UVs.
// 0.0 is no offset, 1.0 is half a pixel offset
uniform float uv_offset_bias;

in float v_angle[];
in vec4 v_color[];
in vec2 v_size[];
in float v_texture[];

out vec2 gs_uv;
out vec4 gs_color;

void main() {
    // Get center of the sprite
    vec3 center = gl_in[0].gl_Position.xyz;
    vec2 hsize = v_size[0] / 2.0;
    float angle = radians(v_angle[0]);
    mat2 rot = mat2(
        cos(angle), -sin(angle),
        sin(angle), cos(angle)
    );
    mat4 mvp = window.projection * window.view;
    // Emit a quad with the right position, rotation and texture coordinates

    // Read texture coordinates from UV texture here
    vec2 uv0, uv1, uv2, uv3;
    getSpriteUVs(uv_texture, int(v_texture[0]), uv0, uv1, uv2, uv3);

    // Apply half pixel offset modified by bias.
    // What bias to set depends on the texture filtering mode.
    // Linear can have 1.0 bias while nearest should have 0.0 (unless scale is 1:1)
    // uvs (
    //     0.0, 0.0,
    //     1.0, 0.0,
    //     0.0, 1.0,
    //     1.0, 1.0
    // )
    vec2 hp = 0.5 / textureSize(sprite_texture, 0) * uv_offset_bias;
    uv0 += hp;
    uv1 += vec2(-hp.x, hp.y);
    uv2 += vec2(hp.x, -hp.y);
    uv3 += -hp;

    // Set the out color for all vertices
    gs_color = v_color[0];
    // Upper left
    gl_Position = mvp * vec4(rot * vec2(-hsize.x, hsize.y) + center.xy, center.z, 1.0);
    gs_uv =  uv0;
    EmitVertex();

    // lower left
    gl_Position = mvp * vec4(rot * vec2(-hsize.x, -hsize.y) + center.xy, center.z, 1.0);
    gs_uv = uv2;
    EmitVertex();

    // upper right
    gl_Position = mvp * vec4(rot * vec2(hsize.x, hsize.y) + center.xy, center.z, 1.0);
    gs_uv = uv1;
    EmitVertex();

    // lower right
    gl_Position = mvp * vec4(rot * vec2(hsize.x, -hsize.y) + center.xy, center.z, 1.0);
    gs_uv = uv3;
    EmitVertex();

    EndPrimitive();
}
