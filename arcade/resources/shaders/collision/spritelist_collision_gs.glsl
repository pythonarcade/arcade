#version 330

#define NUM_POINTS 8

layout (points) in;
layout (line_strip, max_vertices = 16) out;

// Texture containing the hit box points
uniform sampler2D hit_box_point_tex;
// Number of hit box points
float num_hit_box_points;

// The point to pick sprites from
uniform vec2 point;

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

in vec2 v_size[1];
in float v_angle[1];
out vec4 color;

// Read the hit box points from the texture
vec2[8] read_hit_box_points(sampler2D smp, int slot) {
    slot *= 4;
    return vec2[8](
        texelFetch(smp, ivec2(slot, 0.0), 0).xy,
        texelFetch(smp, ivec2(slot, 0.0), 0).zw,
        texelFetch(smp, ivec2(slot + 1, 0.0), 0).xy,
        texelFetch(smp, ivec2(slot + 1, 0.0), 0).zw,
        texelFetch(smp, ivec2(slot + 2, 0.0), 0).xy,
        texelFetch(smp, ivec2(slot + 2, 0.0), 0).zw,
        texelFetch(smp, ivec2(slot + 3, 0.0), 0).xy,
        texelFetch(smp, ivec2(slot + 3, 0.0), 0).zw
    );
}

bool line_intersects(vec2 p1, vec2 p2, vec2 p3, vec2 p4) {
    float d = (p4.y - p3.y) * (p2.x - p1.x) - (p4.x - p3.x) * (p2.y - p1.y);
    if (d == 0.0) {
        return false;
    }
    float u = ((p4.x - p3.x) * (p1.y - p3.y) - (p4.y - p3.y) * (p1.x - p3.x)) / d;
    float v = ((p2.x - p1.x) * (p1.y - p3.y) - (p2.y - p1.y) * (p1.x - p3.x)) / d;
    return (u >= 0.0 && u <= 1.0) && (v >= 0.0 && v <= 1.0);
}

void main() {
    // Unpack in values to more readable variables
    vec2 pos = gl_in[0].gl_Position.xy;
    vec2 size = v_size[0];
    float angle = radians(v_angle[0]);
    mat2 rot = mat2(
        cos(angle), sin(angle),
        -sin(angle), cos(angle)
    );
    mat4 mvp = window.projection * window.view;

    // Get the hit box points from the texture
    vec2[8] p = read_hit_box_points(hit_box_point_tex, int(gl_PrimitiveIDIn));
    // Move and roate the points
    for (int i = 0; i < NUM_POINTS; i++) {
        p[i] = rot * p[i] + pos;
    }
    vec2 collider[4] = vec2[4](
        point + vec2(50, 50.0),
        point + vec2(50.0, -50.0),
        point + vec2(-50, -50),
        point + vec2(-50, 50)
    );

    // color = vec4(1.0, 0.0, 0.0, 1.0);
    color = vec4(0.0, 0.0, 0.0, .0);

    // Check if the point is inside the hit box
    bool found = false;
    for (int c = 0; c < 4; c++) {
        for (int i = 0; i < 8; i++) {
            if (line_intersects(p[i], p[(i + 1) % 8], collider[c], collider[(c + 1) % 4])) {
                color = vec4(1.0, 1.0, 1.0, 1.0);
                found = true;
                break;
            }
            if (found) {
                break;
            }
        }
    }

    gl_Position = mvp * vec4(p[0], 0.0, 1.0);
    EmitVertex();
    gl_Position = mvp * vec4(p[1], 0.0, 1.0);
    EmitVertex();
    gl_Position = mvp * vec4(p[2], 0.0, 1.0);
    EmitVertex();
    gl_Position = mvp * vec4(p[3], 0.0, 1.0);
    EmitVertex();
    gl_Position = mvp * vec4(p[4], 0.0, 1.0);
    EmitVertex();
    gl_Position = mvp * vec4(p[5], 0.0, 1.0);
    EmitVertex();
    gl_Position = mvp * vec4(p[6], 0.0, 1.0);
    EmitVertex();
    gl_Position = mvp * vec4(p[7], 0.0, 1.0);
    EmitVertex();
    gl_Position = mvp * vec4(p[0], 0.0, 1.0);
    EmitVertex();
    EndPrimitive();

    // AABB lies
    // vec2 min_point = vec2(0.0);
    // vec2 max_point = vec2(0.0);
    // get_bbox_for_points(p, min_point, max_point);

    // // Upper right
    // gl_Position = mvp * vec4(pos + max_point, 0.0, 1.0);
    // EmitVertex();
    // // Lower right
    // gl_Position = mvp * vec4(pos + vec2(max_point.x, min_point.y), 0.0, 1.0);
    // EmitVertex();
    // // Lower left
    // gl_Position = mvp * vec4(pos + min_point, 0.0, 1.0);
    // EmitVertex();
    // // Upper left
    // gl_Position = mvp * vec4(pos + vec2(min_point.x, max_point.y), 0.0, 1.0);
    // EmitVertex();
    // // Upper right (repeat, complete strip)
    // gl_Position = mvp * vec4(pos + max_point, 0.0, 1.0);
    // EmitVertex();
}
