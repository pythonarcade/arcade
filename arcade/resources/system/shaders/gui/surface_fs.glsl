#version 330

uniform sampler2D ui_texture;

in vec2 uv;
in vec4 v_color;
out vec4 fragColor;

void main() {
    fragColor = texture(ui_texture, uv) * v_color;
    //fragColor = v_color;
}
