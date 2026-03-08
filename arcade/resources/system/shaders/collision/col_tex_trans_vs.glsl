#version 330
// Texture version if collision shader

#include :system:shaders/lib/sprite.glsl

uniform sampler2D pos_angle_data;
uniform sampler2D size_data;
uniform isampler2D index_data;

out vec2 pos;
out vec2 size;

void main() {
    int index = getInstanceIndex(index_data, gl_VertexID);
    vec4 _pos_rot = getInstancePosRot(pos_angle_data, index);
    vec2 _size = getInstanceSize(size_data, index);  

    pos = _pos_rot.xy;
    size = _size.xy;
}
