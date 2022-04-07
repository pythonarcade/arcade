void mainImage(out vec4 fragColor, in vec2 fragCoord) {

    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = fragCoord/iResolution.xy;

    // How far is the current pixel from the origin (0, 0)
    float distance = length(uv);

    // Default our color to white
    vec3 color = vec3(1.0, 1.0, 1.0);

    // If we are more than 20% of the screen away from origin, use black.
    if (distance > 0.2)
        color = vec3(0.0, 0.0, 0.0);

    // Output to the screen
    fragColor = vec4(color, 1.0);
}