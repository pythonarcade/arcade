#version 330
layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform mat4 Projection;
// [w, h, tilt]
uniform vec3 shape;

void main() {
    // Get center of the circle
    vec2 center = gl_in[0].gl_Position.xy;

    // Calculate rotation/tilt
    float angle = radians(shape.z);
    mat2 rot = mat2(
        cos(angle), -sin(angle),
        sin(angle),  cos(angle)
    );
    vec2 size = shape.xy / 2.0;

    // First outer vertex
    vec2 p1 = rot * (center + vec2(-size.x,  size.y));
    vec2 p2 = rot * (center + vec2(-size.x, -size.y));
    vec2 p3 = rot * (center + vec2( size.x,  size.y));
    vec2 p4 = rot * (center + vec2( size.x, -size.y));

    gl_Position = Projection * vec4(p1, 0.0, 1.0);
    EmitVertex();
    gl_Position = Projection * vec4(p2, 0.0, 1.0);
    EmitVertex();
    gl_Position = Projection * vec4(p3, 0.0, 1.0);
    EmitVertex();
    gl_Position = Projection * vec4(p4, 0.0, 1.0);
    EmitVertex();

    EndPrimitive();
}
