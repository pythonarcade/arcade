#version 330

// The old atlas texture.
uniform sampler2D atlas_old;

out vec4 fragColor;
in vec2 uv;

void main() {
    fragColor = texture(atlas_old, uv);
}
