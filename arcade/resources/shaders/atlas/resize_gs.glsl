#version 330

// The render target for this program is the new
// texture atlas texture

// Old and new texture coordiantes
uniform sampler2D atlas_old;
uniform sampler2D atlas_new;
uniform sampler2D texcoords_old;
uniform sampler2D texcoords_new;
uniform mat4 projection;

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

out vec2 uv;

void main() {
    // Get the texture sizes
    ivec2 size_old = textureSize(atlas_old, 0).xy;
    ivec2 size_new = textureSize(atlas_new, 0).xy;

    // One pixel delta in texture coords
    // We need this to include the texture borders (copy repeating data)
    vec2 delta_old = vec2(1.0) / size_old;

    vec4 data_old = texelFetch(texcoords_old, ivec2(gl_PrimitiveIDIn, 0), 0);
    vec4 data_new = texelFetch(texcoords_new, ivec2(gl_PrimitiveIDIn, 0), 0);

    // Create quads from the new texture coordinates
    vec2 pos = data_new.xy * size_new - vec2(1, 1);
    vec2 size = data_new.zw * size_new + vec2(2.0, 2.0);

    // Map these with the old texture coordiantes
    vec2 tex_offset = (data_old.xy - delta_old)  * vec2(1.0, -1.0);
    vec2 tex_size = (data_old.zw + delta_old * 2.0) * vec2(1.0, -1.0);;

    // upper left
    uv = tex_offset + vec2(0.0, tex_size.y);
    gl_Position = projection * vec4(pos + vec2(0.0, size.y), 0.0, 1.0);
    EmitVertex();

    // lower left
    uv = tex_offset;
    gl_Position = projection * vec4(pos, 0.0, 1.0);
    EmitVertex();

    // upper right
    uv = tex_offset + vec2(tex_size.x, tex_size.y);
    gl_Position = projection * vec4(pos + vec2(size.x, size.y), 0.0, 1.0);
    EmitVertex();

    // lower right
    uv = tex_offset + vec2(tex_size.x, 0.0);
    gl_Position = projection * vec4(pos + vec2(size.x, 0.0), 0.0, 1.0);
    EmitVertex();

    EndPrimitive();
}
