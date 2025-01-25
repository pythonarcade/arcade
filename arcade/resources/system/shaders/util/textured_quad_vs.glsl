#version 330

in vec2 in_uv;
in vec2 in_vert;

out vec2 out_uv;

void main(){
    out_uv = in_uv;
    gl_Position = vec4(in_vert, 0.0, 1.0);
}