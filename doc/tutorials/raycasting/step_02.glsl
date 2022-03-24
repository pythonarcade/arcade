void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 normalizedFragCoord = fragCoord/iResolution.xy;
    vec4 inColor = texture(iChannel0, normalizedFragCoord);
    if (inColor.a > 0.0)
        // Set to a red color
        fragColor = vec4(1.0, 0.0, 0.0, 1.0);
    else
        // Set to a blue color
        fragColor = vec4(0.0, 0.0, 1.0, 1.0);
}
