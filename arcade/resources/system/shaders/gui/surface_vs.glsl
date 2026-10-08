#version 330

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

// Transform applied to the whole surface geometry.
// This allows animating the surface as a whole (translation, rotation,
// scaling and fading) similar to how sprites are transformed.
uniform vec2 pos;     // Translation offset applied to every vertex
uniform float angle;  // Rotation in radians around ``center``
uniform vec2 scale;   // Scale factor around ``center``
uniform vec2 center;  // Point to rotate and scale around (in surface coords)
uniform vec4 color;   // Global color multiplier (fading / tinting)

in vec3 in_pos;
in vec2 in_uv;
in vec4 in_color;

out vec2 uv;
out vec4 v_color;

void main() {
    // Move the vertex into local space around ``center``
    vec2 local = in_pos.xy - center;

    // Apply scale
    local *= scale;

    // Apply rotation
    float s = sin(angle);
    float c = cos(angle);
    vec2 rotated = vec2(
        local.x * c - local.y * s,
        local.x * s + local.y * c
    );

    // Move back from local space and apply the translation offset
    vec2 world = rotated + center + pos;

    gl_Position = window.projection * window.view * vec4(world, in_pos.z, 1.0);
    uv = in_uv;
    // The composite uses premultiplied-alpha blending (ONE, ONE_MINUS_SRC_ALPHA),
    // so the global color multiplier has to be premultiplied as well:
    // fading (color.a) must scale the color channels, not just the alpha channel.
    v_color = in_color * vec4(color.rgb * color.a, color.a);
}
