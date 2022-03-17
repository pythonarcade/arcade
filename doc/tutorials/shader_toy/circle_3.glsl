void mainImage(out vec4 fragColor, in vec2 fragCoord) {

    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = fragCoord/iResolution.xy;

    // Position of fragment relative to center of screen
    vec2 pos = uv - 0.5;
    // Adjust y by aspect ratio
    pos.y /= iResolution.x/iResolution.y;

    // How far is the current pixel from the origin (0, 0)
    float distance = length(pos);
    float scale = 0.02;
    float fade = 1.1;
    float strength = pow(1.0 / distance * scale, fade);

    // Default our color to white
    vec3 color = strength * vec3(1.0, 0.5, 0);

    // Tone mapping
    color = 1.0 - exp( -color );

    // Output to the screen
    fragColor = vec4(color, 1.0);
}