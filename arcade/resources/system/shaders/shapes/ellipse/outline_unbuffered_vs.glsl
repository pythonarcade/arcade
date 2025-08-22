#version 330

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

uniform vec2 center;
uniform int segments;
// [w, h, tilt, thickness]
uniform vec4 shape;

const float PI = 3.141592;

void main() {
    // Two triangles per line segment of the outline
    int segment_id = gl_VertexID / 6;
    int vertex_id = gl_VertexID % 6;

    // Calculate rotation/tilt
    float angle = radians(shape.z);
    mat2 rot = mat2(
        cos(angle), -sin(angle),
        sin(angle),  cos(angle)
    );

    // sin(v), cos(v) travels clockwise around the circle starting at 0, 1 (top of circle)
    float st = PI * 2.0 / float(segments);

    // calculate the four points of the line segment
    // Inner and outer points for the start of line segment
    vec2 p0 = vec2(sin(float(segment_id) * st), cos(float(segment_id) * st)) * shape.xy;
    vec2 p1 = vec2(sin(float(segment_id) * st), cos(float(segment_id) * st)) * (shape.xy - vec2(shape.w));

    // Inner and outer points for the end of line segment
    vec2 p2 = vec2(sin((float(segment_id) + 1.0) * st), cos((float(segment_id) + 1.0) * st)) * shape.xy;
    vec2 p3 = vec2(sin((float(segment_id) + 1.0) * st), cos((float(segment_id) + 1.0) * st)) * (shape.xy - vec2(shape.w));

    vec2 position[6] = vec2[6](
        p1, p0, p2, // first triangle
        p1, p2, p3  // second triangle
    );
    mat4 mvp = window.projection * window.view;
    gl_Position = mvp * vec4(rot * position[vertex_id] + center, 0.0, 1.0);
}
