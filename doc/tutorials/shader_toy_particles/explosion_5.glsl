// Origin of the particles
uniform vec2 pos;

// Constants

// Number of particles
const float PARTICLE_COUNT = 100.0;
// Max distance the particle can be from the position.
// Normalized. (So, 0.3 is 30% of the screen.)
const float MAX_PARTICLE_DISTANCE = 0.3;
// Size of each particle. Normalized.
const float PARTICLE_SIZE = 0.004;
// Time for each burst cycle, in seconds.
const float BURST_TIME = 2.0;
// Particle brightness
const float DEFAULT_BRIGHTNESS = 0.0005;
// How many times to the particles twinkle
const float TWINKLE_SPEED = 10.0;

const float TWOPI = 6.2832;

// This function will return two pseudo-random numbers given an input seed.
// The result is in polar coordinates, to make the points random in a circle
// rather than a rectangle.
vec2 Hash12_Polar(float t) {
  float angle = fract(sin(t * 674.3) * 453.2) * TWOPI;
  float distance = fract(sin((t + angle) * 724.3) * 341.2);
  return vec2(sin(angle), cos(angle)) * distance;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    // Normalized pixel coordinates (from 0 to 1)
    // Origin of the particles
    vec2 npos = (pos - .5 * iResolution.xy) / iResolution.y;
    // Position of current pixel we are drawing
    vec2 uv = (fragCoord- .5 * iResolution.xy) / iResolution.y;

    // Re-center based on input coordinates, rather than origin.
    uv -= npos;

    // Default alpha is transparent.
    float alpha = 0.0;

    // 0.0 - 1.0 normalized fraction representing how far along in the explosion we are.
    // Auto resets if time goes beyond burst time. This causes the explosion to cycle.
    float timeFract = fract(iTime * 1 / BURST_TIME);

    // Loop for each particle
    for (float i= 0.; i < PARTICLE_COUNT; i++) {
        // Direction of particle + speed
        float seed = i + 1.0;
        vec2 dir = Hash12_Polar(seed);
        // Get position based on direction, magnitude, and explosion size
        // Adjust based on time scale. (0.0-1.0)
        vec2 particlePosition = dir * MAX_PARTICLE_DISTANCE * timeFract;
        // Distance of this pixel from that particle
        float d = length(uv - particlePosition);
        // Add glow based on distance
        float brightness = DEFAULT_BRIGHTNESS * (sin(timeFract * TWINKLE_SPEED + i) * .5 + .5);
        alpha += brightness / d;
    }
    // Output to screen
    fragColor = vec4(1.0, 1.0, 1.0, alpha * (1.0 - timeFract));
}
