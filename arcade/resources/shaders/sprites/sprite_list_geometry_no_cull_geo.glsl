#version 330
layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform Projection {
    uniform mat4 matrix;
} proj;

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
    vec2 center = gl_in[0].gl_Position.xy;
    vec2 hsize = v_size[0] / 2.0;
    float angle = radians(v_angle[0]);
    mat2 rot = mat2(
        cos(angle), sin(angle),
        -sin(angle), cos(angle)
    );

    // Emit a quad with the right position, rotation and texture coordinates
    // Read texture coordinates from UV texture here
    vec4 uv_data = texelFetch(uv_texture, ivec2(v_texture[0], 0), 0);
    vec2 tex_offset = uv_data.xy;
    vec2 tex_size = uv_data.zw;

    // Upper left
    gl_Position = proj.matrix * vec4(rot * vec2(-hsize.x, hsize.y) + center, 0.0, 1.0);
    gs_uv =  (vec2(0.0, tex_size.y) + tex_offset) * vec2(1.0, -1.0);
    gs_color = v_color[0];
    EmitVertex();

    // lower left
    gl_Position = proj.matrix * vec4(rot * vec2(-hsize.x, -hsize.y) + center, 0.0, 1.0);
    gs_uv = tex_offset * vec2(1.0, -1.0);
    gs_color = v_color[0];
    EmitVertex();

    // upper right
    gl_Position = proj.matrix * vec4(rot * vec2(hsize.x, hsize.y) + center, 0.0, 1.0);
    gs_uv = (tex_size + tex_offset) * vec2(1.0, -1.0);
    gs_color = v_color[0];
    EmitVertex();

    // lower right
    gl_Position = proj.matrix * vec4(rot * vec2(hsize.x, -hsize.y) + center, 0.0, 1.0);
    gs_uv = (vec2(tex_size.x, 0.0) + tex_offset) * vec2(1.0, -1.0);
    gs_color = v_color[0];
    EmitVertex();

    EndPrimitive();
}
