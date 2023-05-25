#version 430

// Set up our compute groups
layout(local_size_x=COMPUTE_SIZE_X, local_size_y=COMPUTE_SIZE_Y) in;

// Input uniforms go here if you need them.
// Some examples:
//uniform vec2 screen_size;
//uniform vec2 force;
//uniform float frame_time;

// Structure of the star data
struct Star
{
    vec4 pos;
    vec4 vel;
    vec4 color;
};

// Input buffer
layout(std430, binding=0) buffer stars_in
{
    Star stars[];
} In;

// Output buffer
layout(std430, binding=1) buffer stars_out
{
    Star stars[];
} Out;

void main()
{
    int curStarIndex = int(gl_GlobalInvocationID);

    Star in_star = In.stars[curStarIndex];

    vec4 p = in_star.pos.xyzw;
    vec4 v = in_star.vel.xyzw;

    // Move the star according to the current force
    p.xy += v.xy;

    // Calculate the new force based on all the other bodies
    for (int i=0; i < In.stars.length(); i++) {
        // If enabled, this will keep the star from calculating gravity on itself
        // However, it does slow down the calcluations do do this check.
        //  if (i == x)
        //      continue;

        // Calculate distance squared
        float dist = distance(In.stars[i].pos.xyzw.xy, p.xy);
        float distanceSquared = dist * dist;

        // If stars get too close the fling into never-never land.
        // So use a minimum distance
        float minDistance = 0.02;
        float gravityStrength = 0.3;
        float simulationSpeed = 0.002;
        float force = min(minDistance, gravityStrength / distanceSquared) * -simulationSpeed;

        vec2 diff = p.xy - In.stars[i].pos.xyzw.xy;
        // We should normalize this I think, but it doesn't work.
        //  diff = normalize(diff);
        vec2 delta_v = diff * force;
        v.xy += delta_v;
    }


    Star out_star;
    out_star.pos.xyzw = p.xyzw;
    out_star.vel.xyzw = v.xyzw;

    vec4 c = in_star.color.xyzw;
    out_star.color.xyzw = c.xyzw;

    Out.stars[curStarIndex] = out_star;
}
