#version 330

#define PI 3.1415926535897932384626433832795
#define MIN_SEGMENTS 16
#define MAX_SEGMENTS 85

layout (points) in;
// TODO: We might want to increase the number of emitted verties, but core 3.3 says 256 is min requirement.
// TODO: Normally 4096 is supported, but let's stay on the safe side
layout (triangle_strip, max_vertices = 256) out;

uniform Projection {
    uniform mat4 matrix;
} proj;

uniform int segments;
// [w, h, tilt]
uniform vec3 shape;

void main() {
    // Get center of the circle
    vec2 center = gl_in[0].gl_Position.xy;
    int segments_selected = 0;

    // Calculate rotation/tilt
    float angle = radians(shape.z);
    mat2 rot = mat2(
        cos(angle), -sin(angle),
        sin(angle),  cos(angle)
    );

    if (segments > 0) {
        // The user defined number of segments. Clamp it.
        segments_selected = segments;
    } else {
        // Estimate the number of segments needed based on size
        segments_selected = int(2.0 * PI * max(shape.x, shape.y) / 10.0);
    }
    // Clamp number of segments
    segments_selected = clamp(segments_selected, MIN_SEGMENTS, MAX_SEGMENTS);

    // sin(v), cos(v) travels clockwise around the circle starting at 0, 1 (top of circle)
    float step = PI * 2 / segments_selected;

    for (int i = 0; i < segments_selected; i++) {
        gl_Position = proj.matrix * vec4(center, 0.0, 1.0);
        EmitVertex();

        // Calculate the ellipse/circle using 0, 0 as origin
        vec2 p1 = vec2(sin((i + 1) * step), cos((i + 1) * step)) * shape.xy;
        // Rotate the circle and then add translation to get the right origin
        gl_Position = proj.matrix * vec4((rot * p1) + center, 0.0, 1.0);
        EmitVertex();

        // Calculate the ellipse/circle using 0, 0 as origin
        vec2 p2 = vec2(sin(i * step), cos(i * step)) * shape.xy;
        // Rotate the circle and then add translation to get the right origin
        gl_Position = proj.matrix * vec4((rot * p2) + center, 0.0, 1.0);
        EmitVertex();

        EndPrimitive();
    }
}
