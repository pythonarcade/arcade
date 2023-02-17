// Fetch texture coordiantes from uv texture
void getSpriteUVs(sampler2D uvData, int texture_id, out vec2 uv0, out vec2 uv1, out vec2 uv2, out vec2 uv3) {
    texture_id *= 2;
    // Calculate the position in the texture. Basic "line wrapping".
    ivec2 t_size = textureSize(uvData, 0);
    ivec2 pos = ivec2(texture_id % t_size.x, texture_id / t_size.x);
    // Fetch the two upper texture coordinates from the float32 texture
    vec4 data_1 = texelFetch(uvData, pos, 0);
    // Fetch the two upper texture coordinates from the float32 texture
    vec4 data_2 = texelFetch(uvData, pos + ivec2(1, 0), 0);
    // Distribute to out values
    uv0 = data_1.xy;
    uv1 = data_1.zw;
    uv2 = data_2.xy;
    uv3 = data_2.zw;
}
