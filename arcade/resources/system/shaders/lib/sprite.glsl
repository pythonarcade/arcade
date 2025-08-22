// Fetch texture coordinates from uv texture
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

// Functions for fetching per-instance data from textures.
// These are used with the shader program that uses instancing to render sprites
// meaning there is no geo shader involved. This should work for WebGL.
vec4 getInstancePosRot(sampler2D posData, int index) {
    return texelFetch(posData, ivec2(index % 256, index / 256), 0);
}

vec2 getInstanceSize(sampler2D sizeData, int index) {
    return texelFetch(sizeData, ivec2(index % 256, index / 256), 0).xy;
}

vec4 getInstanceColor(sampler2D colorData, int index) {
    return texelFetch(colorData, ivec2(index % 256, index / 256), 0);
}

int getInstanceTextureId(sampler2D textureIdData, int index) {
    return int(texelFetch(textureIdData, ivec2(index % 256, index / 256), 0).x);
}

int getInstanceIndex(isampler2D indexData, int index) {
    return texelFetch(indexData, ivec2(index % 256, index / 256), 0).x;
}
