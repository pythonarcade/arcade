#version 430

layout(local_size_x=COMPUTE_SIZE_X, local_size_y=COMPUTE_SIZE_Y) in;

uniform vec2 screen_size;
uniform vec2 force;
uniform float frame_time;

struct Ball
{
    vec4 pos;
    vec4 vel;
    vec4 col;
};

layout(std430, binding=0) buffer balls_in
{
    Ball balls[];
} In;
layout(std430, binding=1) buffer balls_out
{
    Ball balls[];
} Out;

void main()
{
    int x = int(gl_GlobalInvocationID);

    Ball in_ball = In.balls[x];

    vec4 p = in_ball.pos.xyzw;
    vec4 v = in_ball.vel.xyzw;

    p.xy += v.xy;

    float rad = p.w * 0.5;
    if (p.x - rad <= 0.0)
    {
        p.x = rad;
        v.x *= -0.98;
    }
    else if (p.x + rad >= screen_size.x)
    {
        p.x = screen_size.x - rad;
        v.x *= -0.98;
    }

    if (p.y - rad <= 0.0)
    {
        p.y = rad;
        v.y *= -0.98;
    }
    else if (p.y + rad >= screen_size.y)
    {
        p.y = screen_size.y - rad;
        v.y *= -0.98;
    }
    v.xy += force * frame_time;

    Ball out_ball;
    out_ball.pos.xyzw = p.xyzw;
    out_ball.vel.xyzw = v.xyzw;

    vec4 c = in_ball.col.xyzw;
    out_ball.col.xyzw = c.xyzw;

    Out.balls[x] = out_ball;
}
