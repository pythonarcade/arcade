#version 330

uniform sampler2D ui_texture;

in vec2 uv;
out vec4 fragColor;

void main() {
    fragColor = texture(ui_texture, uv);
}
