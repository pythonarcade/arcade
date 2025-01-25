#version 330
layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

uniform vec2 position;

in float vs_radius[];
in float vs_attenuation[];
in vec3 vs_color[];

out vec2 uv;
out float attenuation;
out vec3 color;

void main() {
    vec2 center = gl_in[0].gl_Position.xy;
    float radius = vs_radius[0];

    gl_Position = window.projection * window.view * vec4(center + vec2(-radius, radius) + position, 0.0, 1.0);
    uv = vec2(0.0, 1.0);
    attenuation = vs_attenuation[0];
    color = vs_color[0];
    EmitVertex();

    gl_Position = window.projection * window.view * vec4(center  + vec2(-radius, -radius) + position, 0.0, 1.0);
    uv = vec2(0.0, 0.0);
    attenuation = vs_attenuation[0];
    color = vs_color[0];
    EmitVertex();

    gl_Position = window.projection * window.view * vec4(center + vec2(radius, radius) + position, 0.0, 1.0);
    uv = vec2(1.0, 1.0);
    attenuation = vs_attenuation[0];
    color = vs_color[0];
    EmitVertex();

    gl_Position = window.projection * window.view * vec4(center + vec2(radius, -radius) + position, 0.0, 1.0);
    uv = vec2(1.0, 0.0);
    attenuation = vs_attenuation[0];
    color = vs_color[0];
    EmitVertex();

    EndPrimitive();
}
