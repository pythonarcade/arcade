#version 330

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

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

    // Emit quad as triangle strip
    vec2 p1 = rot * vec2(-size.x,  size.y);
    vec2 p2 = rot * vec2(-size.x, -size.y);
    vec2 p3 = rot * vec2( size.x,  size.y);
    vec2 p4 = rot * vec2( size.x, -size.y);

    gl_Position = window.projection * window.view * vec4(p1 + center, 0.0, 1.0);
    EmitVertex();
    gl_Position = window.projection * window.view * vec4(p2 + center, 0.0, 1.0);
    EmitVertex();
    gl_Position = window.projection * window.view * vec4(p3 + center, 0.0, 1.0);
    EmitVertex();
    gl_Position = window.projection * window.view * vec4(p4 + center, 0.0, 1.0);
    EmitVertex();

    EndPrimitive();
}
