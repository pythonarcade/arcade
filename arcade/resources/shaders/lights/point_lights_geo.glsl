#version 330
layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform Projection {
    uniform mat4 matrix;
} proj;

uniform vec2 position;

in float vs_radius[1];
in float vs_attenuation[1];
in vec3 vs_color[1];

out vec2 uv;
out float attenuation;
out vec3 color;

void main() {
    vec2 center = gl_in[0].gl_Position.xy;
    float radius = vs_radius[0];

    gl_Position = proj.matrix * vec4(center + vec2(-radius, radius) + position, 0.0, 1.0);
    uv = vec2(0.0, 1.0);
    attenuation = vs_attenuation[0];
    color = vs_color[0];
    EmitVertex();

    gl_Position = proj.matrix * vec4(center  + vec2(-radius, -radius) + position, 0.0, 1.0);
    uv = vec2(0.0, 0.0);
    attenuation = vs_attenuation[0];
    color = vs_color[0];
    EmitVertex();

    gl_Position = proj.matrix * vec4(center + vec2(radius, radius) + position, 0.0, 1.0);
    uv = vec2(1.0, 1.0);
    attenuation = vs_attenuation[0];
    color = vs_color[0];
    EmitVertex();

    gl_Position = proj.matrix * vec4(center + vec2(radius, -radius) + position, 0.0, 1.0);
    uv = vec2(1.0, 0.0);
    attenuation = vs_attenuation[0];
    color = vs_color[0];
    EmitVertex();

    EndPrimitive();
}
