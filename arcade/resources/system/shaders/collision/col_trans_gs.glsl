#version 330

layout(points) in;
layout(points, max_vertices=1) out;

uniform vec2 check_pos;
uniform vec2 check_size;

in vec2 pos[];
in vec2 size[];

out int spriteIndex;

void main() {
    // Calculate the distance between the sprite center
    // and the point we want to check
    float dist = distance(pos[0], check_pos);

    // Get the maximum x and y size
    // max() works per component
    vec2 size = max(size[0], check_size);

    // Destroy the sprite if too far away
    if (dist < max(size.x, size.y) * 1.42) {
        // Set the sprite index to the current primitive id
        // We are only processing points, so it will match
        // the spritelist index
        spriteIndex = int(gl_PrimitiveIDIn);
        EmitVertex();
    }

}
