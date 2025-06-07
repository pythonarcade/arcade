#version 330

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

uniform float line_width;

in vec2 in_vert;
in vec4 in_instance_pos;

vec2 lineNormal2D(vec2 start, vec2 end) {
    vec2 n = end - start;
    return normalize(vec2(-n.y, n.x));
}

void main() {
    vec2 line_start = in_instance_pos.xy;
    vec2 line_end = in_instance_pos.zw;

    vec2 normal = lineNormal2D(line_start, line_end) * line_width / 2.0;
    mat4 mvp = window.projection * window.view;
    vec2 positions[4] = vec2[4](
        line_start + normal,
        line_start - normal,
        line_end + normal,
        line_end - normal
    );
    gl_Position = mvp * vec4(positions[gl_VertexID % 4], 0.0, 1.0);
}
