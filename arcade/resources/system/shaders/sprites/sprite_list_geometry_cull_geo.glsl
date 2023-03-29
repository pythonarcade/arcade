#version 330

#include :system:shaders/lib/sprite.glsl

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

uniform sampler2D uv_texture;

in float v_angle[];
in vec4 v_color[];
in vec2 v_size[];
in float v_texture[];

out vec2 gs_uv;
out vec4 gs_color;

#define VP_CLIP 1.0


void main() {
    // Get center of the sprite
    vec3 center = gl_in[0].gl_Position.xyz;
    vec2 hsize = v_size[0] / 2.0;
    vec2 hsize_max = vec2(max(v_size[0].x, v_size[0].y)) / 1.5;
    float angle = radians(v_angle[0]);
    mat2 rot = mat2(
        cos(angle), -sin(angle),
        sin(angle),  cos(angle)
    );
    mat4 mvp = window.projection * window.view;
    // Do viewport culling for sprites.
    // We do this in normalized device coordinates to make it simple
    // apply projection to the center point. This is important so we get zooming/scrollig right
    vec2 ct = (mvp * vec4(center.xy, 0.0, 1.0)).xy;
    // We can get away with cheaper calculation of size
    // The length of the diagonal is the cheapest estimation in case rotation is applied
    float st = length(hsize_max * vec2(window.projection[0][0], window.projection[1][1]));
    // Discard sprites outside the viewport
    if ((ct.x + st) < -VP_CLIP || (ct.x - st) > VP_CLIP) return;
    if ((ct.y + st) < -VP_CLIP || (ct.y - st) > VP_CLIP) return;

    // Read texture coordinates from UV texture here
    vec2 uv0, uv1, uv2, uv3;
    getSpriteUVs(uv_texture, int(v_texture[0]), uv0, uv1, uv2, uv3);

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
