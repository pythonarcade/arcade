void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 normalizedCoord = fragCoord/iResolution.xy;
    fragColor = texture(iChannel0, normalizedCoord);
}
