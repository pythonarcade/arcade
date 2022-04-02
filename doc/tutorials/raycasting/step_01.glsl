void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 normalizedFragCoord = fragCoord/iResolution.xy;
    fragColor = texture(iChannel0, normalizedFragCoord);
}
