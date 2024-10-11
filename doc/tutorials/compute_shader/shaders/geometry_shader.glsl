#version 330

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

// Use Arcade's global projection UBO
uniform Projection {
    uniform mat4 matrix;
} proj;


// The outputs from the vertex shader are used as inputs
in vec2 vertex_pos[];
in float vertex_radius[];
in vec4 vertex_color[];

// These are used with EmitVertex to generate four points of
// a quad centered around vertex_pos[0].
out vec2 g_uv;
out vec3 g_color;

void main() {
    vec2 center = vertex_pos[0];
    vec2 hsize = vec2(vertex_radius[0]);

    g_color = vertex_color[0].rgb;

    gl_Position = proj.matrix * vec4(vec2(-hsize.x, hsize.y) + center, 0.0, 1.0);
    g_uv = vec2(0, 1);
    EmitVertex();

    gl_Position = proj.matrix * vec4(vec2(-hsize.x, -hsize.y) + center, 0.0, 1.0);
    g_uv = vec2(0, 0);
    EmitVertex();

    gl_Position = proj.matrix * vec4(vec2(hsize.x, hsize.y) + center, 0.0, 1.0);
    g_uv = vec2(1, 1);
    EmitVertex();

    gl_Position = proj.matrix * vec4(vec2(hsize.x, -hsize.y) + center, 0.0, 1.0);
    g_uv = vec2(1, 0);
    EmitVertex();

    // End geometry emmission
    EndPrimitive();
}

