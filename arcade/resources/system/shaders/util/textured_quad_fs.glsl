#version 330

uniform sampler2D texture0;

in vec2 out_uv;

out vec4 out_colour;

void main(){
    out_colour = texture(texture0, out_uv);
}
