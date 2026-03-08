#version 330

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

uniform vec2 center;
uniform int segments;
// [w, h, tilt]
uniform vec3 shape;

const float PI = 3.141592;

void main() {
    int triangle_id = gl_VertexID / 3;
    int vertex_id = gl_VertexID % 3;

    // Calculate rotation/tilt
    float angle = radians(shape.z);
    mat2 rot = mat2(
        cos(angle), -sin(angle),
        sin(angle),  cos(angle)
    );
    // Calculate the positions for the full triangle in the current segment
    vec2 positions[3] = vec2[3](
        vec2(0.0, 0.0),
        vec2(sin((float(triangle_id) + 1.0) * (PI * 2.0 / float(segments))), 
             cos((float(triangle_id) + 1.0) * (PI * 2.0 / float(segments)))) * shape.xy,
        vec2(sin(float(triangle_id) * (PI * 2.0 / float(segments))), 
             cos(float(triangle_id) * (PI * 2.0 / float(segments)))) * shape.xy
    );

    mat4 mvp = window.projection * window.view;
    vec4 pos = vec4(rot * positions[vertex_id] + center, 0.0, 1.0);
    gl_Position = mvp * pos;
}
