// x, y position of the light
uniform vec2 lightPosition;
// Size of light in pixels
uniform float lightSize;

float terrain(vec2 p)
{
    float barrier = texture(iChannel0, p).a;
    float barrier_stepped = step(0.1, barrier);
    return 1.0 - barrier_stepped;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    // Distance in pixels to the light
    float distanceToLight = length(lightPosition - fragCoord);

    // Normalize the fragment coordinate from (0.0, 0.0) to (1.0, 1.0)
    vec2 normalizedFragCoord = fragCoord/iResolution.xy;

    // Start our mixing variable at 1.0
    float b = 1.0;

    float h = terrain(normalizedFragCoord);
    b *= h;

    // Smoothstep from 0.0 to 1.0 depending on the distance from the light
    b *= 1.0 - smoothstep(0.0, lightSize, distanceToLight);

    // We'll alternate our display between black and whatever is in channel 1
    vec4 blackColor = vec4(0.0, 0.0, 0.0, 1.0);

    // Our fragment color will be somewhere between black and channel 1
    // dependent on the value of b.
    fragColor = mix(blackColor, texture(iChannel1, normalizedFragCoord), b);
}
