#version 330

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

// [w, h, tilt]
uniform vec3 shape;

in vec2 in_vert;
in vec2 in_instance_pos;

void main() {
    float angle = radians(shape.z);
    mat2 rot = mat2(
        cos(angle), -sin(angle),
        sin(angle),  cos(angle)
    );
    // vec2 size = shape.xy / 2.0;
    mat4 mvp = window.projection * window.view;
    vec2 pos = in_instance_pos + (rot * (in_vert * shape.xy));
    gl_Position = mvp * vec4(pos, 0.0, 1.0);
}
