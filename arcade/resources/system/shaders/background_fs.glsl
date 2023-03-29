#version 330

in vec2 frag_uv;

uniform sampler2D backgroundTexture;

uniform mat3 pixelTransform;
uniform float blend;
uniform vec3 color;
uniform vec2 pos;
uniform vec2 size;

out vec4 fragColor;

void main() {
    vec2 texSize = vec2(textureSize(backgroundTexture, 0));
    vec2 adjustedUV = frag_uv * size;

    vec2 adjusted = (pixelTransform * vec3(adjustedUV, 1.0)).xy;

    adjusted = adjusted / texSize;
    fragColor = texture(backgroundTexture, adjusted);
    fragColor.rgb *= color;
    fragColor.a *= blend;
}
