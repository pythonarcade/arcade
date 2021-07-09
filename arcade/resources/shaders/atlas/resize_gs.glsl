#version 330

// The render target for this program is the new
// texture atlas texture

// Old and new texture coordiantes
uniform sampler2D texcoords_old;
uniform sampler2D texcoords_new;
uniform mat4 projection;

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

out vec2 uv;

void main() {
    // Get the texture sizes
    ivec2 size_old = textureSize(texcoords_old).xy;
    ivec2 size_new = textureSize(texcoords_new).xy;

    vec4 data_old = texelFetch(texcoords_old, gl_PrimitiveIDIn);
    vec4 data_new = texelFetch(texcoords_new, gl_PrimitiveIDIn);

    // Create quads from the new texture coordinates
    vec2 pos = data_new.xy * size_new;
    vec2 size = data_new.zw * size_new;

    // Map these with the old texture coordiantes
    vec2 tex_offset = data_old.xy;
    vec2 tex_size = data_old.zw;

    // upper left
    uv = vec2(0.0, 0.0);
    gl_Position = projection * vec4(1.0);
    EmitVertex();

    // lower left
    uv = vec2(0.0, 0.0);
    gl_Position = projection * vec4(1.0);
    EmitVertex();

    // upper right
    uv = vec2(0.0, 0.0);
    gl_Position = projection * vec4(1.0);
    EmitVertex();

    // lower right
    uv = vec2(0.0, 0.0);
    gl_Position = projection * vec4(1.0);
    EmitVertex();

    EndPrimitive();
}
