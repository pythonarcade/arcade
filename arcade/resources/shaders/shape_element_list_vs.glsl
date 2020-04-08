#version 330

uniform mat4 Projection;
uniform vec2 Position;
uniform float Angle;

in vec2 in_vert;
in vec4 in_color;

out vec4 v_color;

void main() {
    float angle = radians(Angle);
    mat2 rotate = mat2(
        cos(angle), sin(angle),
        -sin(angle), cos(angle)
    );
    gl_Position = Projection * vec4(Position + (rotate * in_vert), 0.0, 1.0);
    v_color = in_color;
}
