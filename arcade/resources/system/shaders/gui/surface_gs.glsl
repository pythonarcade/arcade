#version 330

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

uniform vec2 pos;
uniform vec2 size;
uniform vec4 area;

out vec2 uv;

void main() {
    mat4 mvp = window.projection * window.view;    

    // Clamp the area inside the surface
    // This is the local area inside the surface
    // Format is (x, y, width, height)
    vec2 b1 = clamp(area.xy, vec2(0.0), size);
    vec2 b2 = clamp(area.xy + area.zw, vec2(0.0), size);
    vec4 l_area = vec4(
        clamp(area.xy, vec2(0.0), size),
        b2 - b1
    );

    // Create the 4 corners of the rectangle
    // These are the final/global coordinates rendered
    vec2 p_ll = pos + l_area.xy;
    vec2 p_lr = pos + l_area.xy + vec2(l_area.z, 0.0);
    vec2 p_ul = pos + l_area.xy + vec2(0, l_area.w);;
    vec2 p_ur = pos + l_area.xy + l_area.zw;

    // Calculate the UV coordinates
    float bottom = l_area.y / size.y;
    float left = l_area.x / size.x;
    float top = (l_area.y + l_area.w) / size.y;
    float right = (l_area.x + l_area.z) / size.x;

    gl_Position = mvp * vec4(p_ll, 0.0, 1.0);
    uv = vec2(left, bottom);
    EmitVertex();

    gl_Position = mvp * vec4(p_lr, 0.0, 1.0);
    uv = vec2(right, bottom);
    EmitVertex();

    gl_Position = mvp * vec4(p_ul, 0.0, 1.0);
    uv = vec2(left, top);
    EmitVertex();

    gl_Position = mvp * vec4(p_ur, 0.0, 1.0);
    uv = vec2(right, top);
    EmitVertex();

    EndPrimitive();
}
