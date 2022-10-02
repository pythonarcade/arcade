#version 330
// Geometry shader emitting 9 patch from point

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

uniform sampler2D uv_texture;
uniform float texture_id;

uniform vec2 start;
uniform vec2 end;

uniform vec2 size;
uniform vec2 t_size;

layout(points) in;
layout(triangle_strip, max_vertices = 36) out;

out vec2 uv;

void main() {
    // Get texture coordinates
    vec4 uv_data = texelFetch(uv_texture, ivec2(texture_id, 0), 0);
    vec2 tex_offset = uv_data.xy;
    vec2 tex_size = uv_data.zw;

    // Patch points starting from upper left row by row
    vec2 p1 = vec2(0.0, size.y);
    vec2 p2 = vec2(start.x, size.y);
    vec2 p3 = vec2(size.x - (t_size.x - end.x), size.y);
    vec2 p4 = vec2(size.x, size.y);

    vec2 p5 = vec2(0.0, size.y - start.y);
    vec2 p6 = vec2(start.x, size.y - start.y);
    vec2 p7 = vec2(size.x - (t_size.x - end.x), size.y - start.y);
    vec2 p8 = vec2(size.x, size.y - start.y);

    vec2 p9 = vec2(0.0, start.y);
    vec2 p10 = vec2(start.x, start.y);
    vec2 p11 = vec2(size.x - (t_size.x - end.x), start.y);
    vec2 p12 = vec2(size.x, start.y);

    vec2 p13 = vec2(0.0, 0.0);
    vec2 p14 = vec2(start.x, 0.0);
    vec2 p15 = vec2(size.x - (t_size.x - end.x), 0.0);
    vec2 p16 = vec2(size.x, 0.0);

    // Texture coordinates starting from upper left
    // ----------------------------------
    // 0.001953125,  0.251953125 (offset)
    // 0.25       ,  -0.25       (size)
    // ----------------------------------
    // upper left  : Vec2(x=0.001953125, y=0.001953125)
    // upper right : Vec2(x=0.251953125, y=0.001953125)
    // lower left  : Vec2(x=0.001953125, y=0.251953125)
    // lower right : Vec2(x=0.251953125, y=0.251953125)
    // ----------------------------------
    vec2 start_uv = abs(start / t_size * tex_size);
    vec2 end_uv = abs((t_size - end) / t_size * tex_size);
  
    vec2 t1 = vec2(0.0, tex_size.y) + tex_offset;
    vec2 t2 = vec2(start_uv.x, tex_size.y) + tex_offset;
    vec2 t3 = vec2(tex_size.x - end_uv.x, tex_size.y) + tex_offset;
    vec2 t4 = tex_size + tex_offset;

    vec2 t5 = vec2(0.0, tex_size.y + end_uv.y) + tex_offset;
    vec2 t6 = vec2(start_uv.x, tex_size.y + end_uv.y) + tex_offset;
    vec2 t7 = vec2(tex_size.x - end_uv.x, tex_size.y + end_uv.y) + tex_offset;
    vec2 t8 = tex_size + tex_offset + vec2(0.0, end_uv.y);

    float y_offset = tex_offset.y - start_uv.y;
    vec2 t9 = vec2(0.0, tex_size.y + y_offset) + tex_offset;
    vec2 t10 = vec2(start_uv.x, tex_size.y + y_offset) + tex_offset;
    vec2 t11 = vec2(tex_size.x - end_uv.x, tex_size.y + y_offset) + tex_offset;
    vec2 t12 = tex_size + tex_offset + vec2(0.0, y_offset);

    y_offset = abs(tex_size.y);
    vec2 t13 = vec2(0.0, tex_size.y + y_offset) + tex_offset;
    vec2 t14 = vec2(start_uv.x, tex_size.y + y_offset) + tex_offset;
    vec2 t15 = vec2(tex_size.x - end_uv.x, tex_size.y + y_offset) + tex_offset;
    vec2 t16 = tex_size + tex_offset + vec2(0.0, y_offset);

    mat4 mvp = window.projection * window.view;
    // First row - two fixed corners + strechy middle - 8 vertices
    // NOTE: This should ideally be done with 3 strips
    // Upper left corner
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

    // Upper middle part
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

    // Upper right corner
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

    // middle row - three strechy parts - 8 vertices
    // left border
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
  
    // Center area
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

    // Right border
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

    // last row - two fixed corners + strechy middle - 8 vertices
    // Lower left corner
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

    // Lower middle part
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

    // Lower right corner
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
