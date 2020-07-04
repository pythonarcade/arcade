#version 330

uniform Projection {
    uniform mat4 matrix;
} proj;
uniform mat3 TextureTransform;

// per vertex
in vec2 in_vert;
in vec2 in_texture;

// per instance
in vec2 in_pos;
in float in_angle;
in vec2 in_size;
in vec4 in_sub_tex_coords;
in vec4 in_color;

out vec2 v_texture;
out vec4 v_color;

void main() {
    mat2 rotate = mat2(
                cos(in_angle), sin(in_angle),
                -sin(in_angle), cos(in_angle)
            );
    vec2 pos;
    pos = in_pos + vec2(rotate * (in_vert * (in_size / 2)));
    gl_Position = proj.matrix * vec4(pos, 0.0, 1.0);

    vec2 tex_offset = in_sub_tex_coords.xy;
    vec2 tex_size = in_sub_tex_coords.zw;

    v_texture = (in_texture * tex_size + tex_offset) * vec2(1, -1);
    vec3 temp = TextureTransform * vec3(v_texture, 1.0);
    v_texture = temp.xy / temp.z;
    v_color = in_color;
}
