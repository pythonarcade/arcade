void mainImage(out vec4 fragColor, in vec2 fragCoord) {

    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = fragCoord/iResolution.xy;

    // Position of fragment relative to center of screen
    vec2 pos = uv - 0.5;
    // Adjust y by aspect ratio
    pos.y /= iResolution.x/iResolution.y;

    // How far is the current pixel from the origin (0, 0)
    float distance = length(pos);

    // Default our color to white
    vec3 color = vec3(1.0, 1.0, 1.0);

    // If we are more than 20% of the screen away from origin, use black.
    if (distance > 0.2)
        color = vec3(0.0, 0.0, 0.0);

    // Output to the screen
    fragColor = vec4(color, 1.0);
}