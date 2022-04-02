#version 330

layout (lines) in;
layout (triangle_strip, max_vertices = 4) out;

uniform Projection {
    uniform mat4 matrix;
} proj;

uniform float line_width;

in vec4 vs_color[];
out vec4 gs_color;

vec2 lineNormal2D(vec2 start, vec2 end) {
    vec2 n = end - start;
    return normalize(vec2(-n.y, n.x));
}

void main() {
    // Get the line segment
    vec2 line_start = gl_in[0].gl_Position.xy;
    vec2 line_end = gl_in[1].gl_Position.xy;

    gs_color = vs_color[0];
    // Calculate normal
    vec2 normal = lineNormal2D(line_start, line_end) * line_width / 2.0;
    gl_Position = proj.matrix * vec4(line_start + normal, 0.0, 1.0);
    EmitVertex();
    gl_Position = proj.matrix * vec4(line_start - normal, 0.0, 1.0);
    EmitVertex();
    gl_Position = proj.matrix * vec4(line_end + normal, 0.0, 1.0);
    EmitVertex();
    gl_Position = proj.matrix * vec4(line_end - normal, 0.0, 1.0);
    EmitVertex();

    EndPrimitive();
}
