#version 330

uniform sampler2D Texture;

in vec2 v_texture;
in vec4 v_color;

out vec4 f_color;

void main() {
    vec4 basecolor = texture(Texture, v_texture);
    basecolor = basecolor * v_color;
    if (basecolor.a == 0.0){
        discard;
    }
    f_color = basecolor;
}
