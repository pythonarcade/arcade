#version 330
layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform mat4 Projection;
uniform mat3 TextureTransform;

in float v_angle[1];
in vec4 v_color[1];
in vec2 v_size[1];
in vec4 v_sub_tex_coords[1];

out vec2 gs_uv;
out vec4 gs_color;

void main() {
    // Get center of the sprite
    vec2 center = gl_in[0].gl_Position.xy;
    vec2 hsize = v_size[0] / 2.0;
    float angle = radians(v_angle[0]);
    mat2 rot = mat2(
        cos(angle), sin(angle),
        -sin(angle), cos(angle)
    );
    // TODO: Viewport culling. compare with size
    // 800 x 0.0025 = 2
    // 600 x 0.00333333 = 2
    //
    // Projection matrix
    // [ 0.0025    0.          0.          0.
    // 0.          0.00333333  0.          0.
    // 0.          0.         -0.00181818  0.
    // -1.        -1.          0.8181818   1.]

    // Emit a quad with the right position, rotation and texture coordinates
    vec2 tex_offset = v_sub_tex_coords[0].xy;
    vec2 tex_size = v_sub_tex_coords[0].zw;

    gl_Position = Projection * vec4(rot * vec2(-hsize.x, hsize.y) + center, 0.0, 1.0);
    vec3 tex1 = TextureTransform * vec3((vec2(0.0, 1.0) * tex_size + tex_offset) * vec2(1, -1), 1.0);
    gs_uv = tex1.xy / tex1.z;
    gs_color = v_color[0];
    EmitVertex();

    gl_Position = Projection * vec4(rot * vec2(-hsize.x, -hsize.y) + center, 0.0, 1.0);
    vec3 tex2 = TextureTransform * vec3((vec2(0.0, 0.0) * tex_size + tex_offset) * vec2(1, -1), 1.0);
    gs_uv = tex2.xy / tex2.z;
    gs_color = v_color[0];
    EmitVertex();

    gl_Position = Projection * vec4(rot * vec2(hsize.x, hsize.y) + center, 0.0, 1.0);
    vec3 tex3 = TextureTransform * vec3((vec2(1.0, 1.0) * tex_size + tex_offset) * vec2(1, -1), 1.0);
    gs_uv = tex3.xy / tex3.z;
    gs_color = v_color[0];
    EmitVertex();

    gl_Position = Projection * vec4(rot * vec2(hsize.x, -hsize.y) + center, 0.0, 1.0);
    vec3 tex4 = TextureTransform * vec3((vec2(1.0, 0.0) * tex_size + tex_offset) * vec2(1, -1), 1.0);
    gs_uv = tex4.xy / tex4.z;
    gs_color = v_color[0];
    EmitVertex();

    EndPrimitive();
}
