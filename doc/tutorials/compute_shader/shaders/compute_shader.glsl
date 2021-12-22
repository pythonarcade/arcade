#version 430

layout(local_size_x=COMPUTE_SIZE_X, local_size_y=COMPUTE_SIZE_Y) in;

// Input uniforms if you need them
//uniform vec2 screen_size;
//uniform vec2 force;
//uniform float frame_time;

// Structure of the ball data
struct Ball
{
    vec4 pos;
    vec4 vel;
    vec4 color;
};

// Input buffer
layout(std430, binding=0) buffer balls_in
{
    Ball balls[];
} In;

// Output buffer
layout(std430, binding=1) buffer balls_out
{
    Ball balls[];
} Out;

void main()
{
    int curBallIndex = int(gl_GlobalInvocationID);

    Ball in_ball = In.balls[curBallIndex];

    vec4 p = in_ball.pos.xyzw;
    vec4 v = in_ball.vel.xyzw;

    p.xy += v.xy;

    for (int i=0; i < In.balls.length(); i++) {
        // If enabled, this will keep the star from calculating gravity on itself
        // However, it does slow down the calcluations do do this check.
        //  if (i == x)
        //      continue;

        // Calculate distance squared
        float dist = distance(In.balls[i].pos.xyzw.xy, p.xy);
        float distanceSquared = dist * dist;

        // If stars get too close the fling into never-never land.
        // So use a minimum distance
        float minDistance = 0.02;
        float gravityStrength = 0.3;
        float simulationSpeed = 0.002;
        float force = min(minDistance, gravityStrength / distanceSquared) * -simulationSpeed;

        vec2 diff = p.xy - In.balls[i].pos.xyzw.xy;
        // We should normalize this I think, but it doesn't work.
        //  diff = normalize(diff);
        vec2 delta_v = diff * force;
        v.xy += delta_v;
    }

    Ball out_ball;
    out_ball.pos.xyzw = p.xyzw;
    out_ball.vel.xyzw = v.xyzw;

    vec4 c = in_ball.color.xyzw;
    out_ball.color.xyzw = c.xyzw;

    Out.balls[curBallIndex] = out_ball;
}
