#define N 150

float terrain(vec2 p)
{
    float barrier = texture(iChannel0, p).a;
    float barrier_stepped = step(0.1, barrier);
    return 1.0 - barrier_stepped;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 p = fragCoord/iResolution.xy;
    vec2 l = iMouse.xy/iResolution.xy;
    vec2 d = p - l;
    float b = 1.0;
    for(float i = 0.0; i < N; i++)
    {
        float t = i / N;
	    float h = terrain(mix(p, l, t));
        b *= h;
    }

    b *= 1.0 - smoothstep(0.0, 0.5, length(d));
    vec4 black = vec4(0.0, 0.0, 0.0, 1.0);
    fragColor = mix(black, texture(iChannel1, p), b);
}
