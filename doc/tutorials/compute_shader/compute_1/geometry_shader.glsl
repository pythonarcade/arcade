#version 330

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

// Use arcade's global projection UBO
uniform Projection {
    uniform mat4 matrix;
} proj;

in vec2 v_pos[];
in vec4 v_col[];
in float v_radius[];

out vec2 g_uv;
out vec3 g_col;

void main() {
    vec2 center = v_pos[0];
    vec2 hsize = vec2(v_radius[0]);

    g_col = v_col[0].rgb;

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

    EndPrimitive();
}

