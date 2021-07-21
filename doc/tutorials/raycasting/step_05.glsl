#define N 500

// x, y position of the light
uniform vec2 lightPosition;
// Size of light in pixels
uniform float lightSize;

float terrain(vec2 samplePoint)
{
    float samplePointAlpha = texture(iChannel0, samplePoint).a;
    float sampleStepped = step(0.1, samplePointAlpha);
    float returnValue = 1.0 - sampleStepped;

    return returnValue;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    float distanceToLight = length(lightPosition - fragCoord);

    vec2 normalizedFragCoord = fragCoord/iResolution.xy;
    vec2 normalizedLightCoord = lightPosition.xy/iResolution.xy;

    float lightAmount = 1.0;
    for(float i = 0.0; i < N; i++)
    {
        // A 0.0 - 1.0 ratio between where our current pixel is, and where the light is
        float t = i / N;
        // Grab a coordinate between where we are and the light
        vec2 castCoord = mix(normalizedFragCoord, normalizedLightCoord, t);
        // Is there something there? If so, we'll assume we are in shadow
	    float shadowAmount = terrain(castCoord);
        // Multiply the light amount.
        // (Multiply in case we want to upgrade to soft shadows)
        lightAmount *= shadowAmount;
    }

    // Find out how much light we have based on the distance to our light
    lightAmount *= 1.0 - smoothstep(0.0, lightSize, distanceToLight);
    // The color black
    vec4 black = vec4(0.0, 0.0, 0.0, 1.0);

    fragColor = mix(black, texture(iChannel1, normalizedFragCoord), lightAmount);
}
