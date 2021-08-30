#version 330

uniform float iTime;
uniform vec2 iMouse;
uniform vec2 iResolution;
uniform sampler2D iChannel0;
uniform sampler2D iChannel1;
uniform sampler2D iChannel2;
uniform sampler2D iChannel3;

in vec2 v_uv;
out vec4 out_color;

$mainfunc

void main() {
    vec4 color;
    mainImage(color, gl_FragCoord.xy);
    out_color = color;
}
