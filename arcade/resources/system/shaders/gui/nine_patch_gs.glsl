#version 330
// Geometry shader emitting 9 patch from point
// This can be simplified somewhat, but the verbose version are easier to maintain

#include :system:shaders/lib/sprite.glsl

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

uniform sampler2D sprite_texture;
uniform sampler2D uv_texture;

uniform float texture_id;

// Lower left: Border in pixels
uniform vec2 start;
// Upper right: Border in pixels
uniform vec2 end;

// The xp position of the patch
uniform vec2 position;
// Size of the patch in pixels
uniform vec2 size;
// Size of the texture in pixels
uniform vec2 t_size;

layout(points) in;
layout(triangle_strip, max_vertices = 36) out;

out vec2 uv;

void main() {
    // Patch points starting from upper left row by row
    vec2 p1 = position + vec2(0.0, size.y);
    vec2 p2 = position + vec2(start.x, size.y);
    vec2 p3 = position + vec2(size.x - (t_size.x - end.x), size.y);
    vec2 p4 = position + vec2(size.x, size.y);

    float y = size.y - (t_size.y - end.y);
    vec2 p5 = position + vec2(0.0, y);
    vec2 p6 = position + vec2(start.x, y);
    vec2 p7 = position + vec2(size.x - (t_size.x - end.x), y);
    vec2 p8 = position + vec2(size.x, y);

    vec2 p9 = position + vec2(0.0, start.y);
    vec2 p10 = position + vec2(start.x, start.y);
    vec2 p11 = position + vec2(size.x - (t_size.x - end.x), start.y);
    vec2 p12 = position + vec2(size.x, start.y);

    vec2 p13 = position + vec2(0.0, 0.0);
    vec2 p14 = position + vec2(start.x, 0.0);
    vec2 p15 = position + vec2(size.x - (t_size.x - end.x), 0.0);
    vec2 p16 = position + vec2(size.x, 0.0);

    // <AtlasRegion 
    //     x=1 y=1 
    //     width=100 height=100
    //     uvs=(
    //         0.001953125, 0.001953125,
    //         0.197265625, 0.001953125,
    //         0.001953125, 0.197265625,
    //         0.197265625, 0.197265625,
    //     )
    // Get texture coordinates
    vec2 uv0, uv1, uv2, uv3;
    vec2 atlas_size = vec2(textureSize(sprite_texture, 0));
    getSpriteUVs(uv_texture, int(texture_id), uv0, uv1, uv2, uv3);

    // Local corner offsets in pixels
    float left = start.x;
    float right = t_size.x - end.x;
    float top = t_size.y - end.y;
    float bottom = start.y;
    // UV offsets to the inner rectangle in the patch
    // This is the global texture coordiante offset in the entire atlas
    vec2 c1 = vec2(left, top) / atlas_size;      // Upper left corner
    vec2 c2 = vec2(right, top) / atlas_size;     // Upper right corner
    vec2 c3 = vec2(left, bottom) / atlas_size;   // Lower left corner
    vec2 c4 = vec2(right, bottom) / atlas_size;  // Lower right corner

    // Texture coordinates for all the points in the patch
    vec2 t1 = uv0;
    vec2 t2 = uv0 + vec2(c1.x, 0.0);
    vec2 t3 = uv1 - vec2(c2.x, 0.0);
    vec2 t4 = uv1;

    vec2 t5 = uv0 + vec2(0.0, c1.y);
    vec2 t6 = uv0 + c1;
    vec2 t7 = uv1 + vec2(-c2.x, c2.y);
    vec2 t8 = uv1 + vec2(0.0, c2.y);

    vec2 t9 = uv2 - vec2(0.0, c3.y);
    vec2 t10 = uv2 + vec2(c3.x, -c3.y);
    vec2 t11 = uv3 - c4;
    vec2 t12 = uv3 - vec2(0.0, c4.y);

    vec2 t13 = uv2;
    vec2 t14 = uv2 + vec2(c3.x, 0.0);
    vec2 t15 = uv3 - vec2(c4.x, 0.0);
    vec2 t16 = uv3;

    mat4 mvp = window.projection * window.view;
    // First row - two fixed corners + strechy middle
    // Upper left corner. Fixed size.
    gl_Position = mvp * vec4(p1, 0.0, 1.0);
    uv = t1;
    EmitVertex();
    gl_Position = mvp * vec4(p5, 0.0, 1.0);
    uv = t5;
    EmitVertex();
    gl_Position = mvp * vec4(p2, 0.0, 1.0);
    uv = t2;
    EmitVertex();
    gl_Position = mvp * vec4(p6, 0.0, 1.0);
    uv = t6;
    EmitVertex();
    EndPrimitive();

    // Upper middle part streches on x axis
    gl_Position = mvp * vec4(p2, 0.0, 1.0);
    uv = t2;
    EmitVertex();
    gl_Position = mvp * vec4(p6, 0.0, 1.0);
    uv = t6;
    EmitVertex();
    gl_Position = mvp * vec4(p3, 0.0, 1.0);
    uv = t3;
    EmitVertex();
    gl_Position = mvp * vec4(p7, 0.0, 1.0);
    uv = t7;
    EmitVertex();
    EndPrimitive();

    // Upper right corner. Fixed size
    gl_Position = mvp * vec4(p3, 0.0, 1.0);
    uv = t3;
    EmitVertex();
    gl_Position = mvp * vec4(p7, 0.0, 1.0);
    uv = t7;
    EmitVertex();
    gl_Position = mvp * vec4(p4, 0.0, 1.0);
    uv = t4;
    EmitVertex();
    gl_Position = mvp * vec4(p8, 0.0, 1.0);
    uv = t8;
    EmitVertex();
    EndPrimitive();

    // Middle row: Two strechy sides + strechy middle
    // left border steching on y axis
    gl_Position = mvp * vec4(p5, 0.0, 1.0);
    uv = t5;
    EmitVertex();
    gl_Position = mvp * vec4(p9, 0.0, 1.0);
    uv = t9;
    EmitVertex();
    gl_Position = mvp * vec4(p6, 0.0, 1.0);
    uv = t6;
    EmitVertex();
    gl_Position = mvp * vec4(p10, 0.0, 1.0);
    uv = t10;
    EmitVertex();
    EndPrimitive();
  
    // Center strechy area
    gl_Position = mvp * vec4(p6, 0.0, 1.0);
    uv = t6;
    EmitVertex();
    gl_Position = mvp * vec4(p10, 0.0, 1.0);
    uv = t10;
    EmitVertex();
    gl_Position = mvp * vec4(p7, 0.0, 1.0);
    uv = t7;
    EmitVertex();
    gl_Position = mvp * vec4(p11, 0.0, 1.0);
    uv = t11;
    EmitVertex();
    EndPrimitive();

    // Right border. Steches on y axis
    gl_Position = mvp * vec4(p7, 0.0, 1.0);
    uv = t7;
    EmitVertex();
    gl_Position = mvp * vec4(p11, 0.0, 1.0);
    uv = t11;
    EmitVertex();
    gl_Position = mvp * vec4(p8, 0.0, 1.0);
    uv = t8;
    EmitVertex();
    gl_Position = mvp * vec4(p12, 0.0, 1.0);
    uv = t12;
    EmitVertex();
    EndPrimitive();

    // Bottom row: two fixed corners + strechy middle
    // Lower left corner. Fixed size
    gl_Position = mvp * vec4(p9, 0.0, 1.0);
    uv = t9;
    EmitVertex();
    gl_Position = mvp * vec4(p13, 0.0, 1.0);
    uv = t13;
    EmitVertex();
    gl_Position = mvp * vec4(p10, 0.0, 1.0);
    uv = t10;
    EmitVertex();
    gl_Position = mvp * vec4(p14, 0.0, 1.0);
    uv = t14;
    EmitVertex();
    EndPrimitive();

    // Lower middle part. Streches on x axis
    gl_Position = mvp * vec4(p10, 0.0, 1.0);
    uv = t10;
    EmitVertex();
    gl_Position = mvp * vec4(p14, 0.0, 1.0);
    uv = t14;
    EmitVertex();
    gl_Position = mvp * vec4(p11, 0.0, 1.0);
    uv = t11;
    EmitVertex();
    gl_Position = mvp * vec4(p15, 0.0, 1.0);
    uv = t15;
    EmitVertex();
    EndPrimitive();

    // Lower right corner. Fixed size
    gl_Position = mvp * vec4(p11, 0.0, 1.0);
    uv = t11;
    EmitVertex();
    gl_Position = mvp * vec4(p15, 0.0, 1.0);
    uv = t15;
    EmitVertex();
    gl_Position = mvp * vec4(p12, 0.0, 1.0);
    uv = t12;
    EmitVertex();
    gl_Position = mvp * vec4(p16, 0.0, 1.0);
    uv = t16;
    EmitVertex();
    EndPrimitive();
}
