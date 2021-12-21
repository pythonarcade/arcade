#version 330

in vec2 g_uv;
in vec3 g_col;

out vec4 out_color;

void main()
{
    if (length(vec2(0.5, 0.5) - g_uv.xy) > 0.25)
    {
        discard;
    }

    vec3 c = g_col.rgb;
    // c.xy += v_uv.xy * 0.05;
    // c.xy += v_pos.xy * 0.75;
    out_color = vec4(c, 1.0);
}
