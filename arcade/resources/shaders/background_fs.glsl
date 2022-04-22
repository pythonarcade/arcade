#version 330

in vec2 frag_uv;

uniform sampler2D backgroundTexture;

uniform mat3 pixelTransform;

uniform float blend = 1;

uniform vec2 pos;
uniform vec2 size;
uniform vec2 bounds;

out vec4 fragColor;

void main() {
    vec2 texSize = vec2(textureSize(backgroundTexture, 0));
    vec2 adjustedUV = frag_uv * size;

    vec2 adjusted = (pixelTransform * vec3(adjustedUV, 1.0)).xy;

    adjusted = adjusted / texSize;
    fragColor = texture(backgroundTexture, adjusted, 0);
    fragColor.a *= blend;
}
