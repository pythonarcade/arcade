#version 330

// The old atlas texture. We copy sections to the new atlas texture
// by render into an fbo with the target texture as the color attachment.
uniform sampler2D atlas_old;

out vec4 fragColor;
in vec2 uv;

void main() {
    fragColor = texture(atlas_old, uv);
}
