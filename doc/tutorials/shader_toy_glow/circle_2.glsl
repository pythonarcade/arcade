void mainImage(out vec4 fragColor, in vec2 fragCoord) {

    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = fragCoord/iResolution.xy;

    // Position of fragment relative to center of screen
    vec2 rpos = uv - 0.5;
    // Adjust y by aspect ratio
    rpos.y /= iResolution.x/iResolution.y;

    // How far is the current pixel from the origin (0, 0)
    float distance = length(rpos);

    // Default our color to white
    vec3 color = vec3(1.0, 1.0, 1.0);

    // Are we are 20% of the screen away from the origin?
    if (distance > 0.2) {
        // Black
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
    } else {
        // White
        fragColor = vec4(1.0, 1.0, 1.0, 1.0);
    }
}