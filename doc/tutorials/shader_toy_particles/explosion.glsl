// Thanks to The Art of Code
// https://www.youtube.com/watch?v=xDxAnguEOn8

uniform vec2 pos;

const float TWOPI = 6.2832;
const float PARTICLE_COUNT = 100.0;
const float TWINKLE_SPEED = 20.0;
const float SPEED = 1.0;
const float BURST_TIME = 2.0;
const float PARTICLE_DISTANCE = 0.3;

// Function to return two pseudo random numbers given an input number
// Result is in polar coordinates to make circular rather than square
// splat.
vec2 Hash12_Polar(float t) {
  float angle = fract(sin(t * 674.3) * 453.2) * TWOPI;
  float distance = fract(sin((t + angle) * 724.3) * 341.2);

  return vec2(sin(angle), cos(angle)) * distance;
}
void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    // Normalized pixel coordinates (from 0 to 1)
    vec2 npos = (pos - .5 * iResolution.xy) / iResolution.y;
    vec2 uv = (fragCoord- .5 * iResolution.xy) / iResolution.y;

    // Move things so the explosion is at the specified coordinates
    uv -= npos;

    float col = 0.;

    float t = fract(iTime * 1 / BURST_TIME);

    for (float i= 0.; i < PARTICLE_COUNT; i++) {
        vec2 dir = Hash12_Polar(i + 1.0);

        float d = length(uv - dir * t * PARTICLE_DISTANCE) ;
       // float d = 1.0;
        //float brightness = mix(.0005, .002, smoothstep(1.5, 0., t));
        float brightness = 0.0005;
        brightness *= sin(t * TWINKLE_SPEED + i) * .5 + .5;
        col += brightness/d;
    }
    // Output to screen
    fragColor = vec4(1.0, 1.0, 1.0, col * (1.0 - t));
}
