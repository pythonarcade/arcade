#version 330

// Sample rate is for sound and can be implemented at a later time
// uniform float     iSampleRate;           // sound sample rate (i.e., 44100)
uniform float     iTime;                 // shader playback time (in seconds)
uniform float     iChannelTime[4];       // channel playback time (in seconds)
uniform vec4      iMouse;                // mouse pixel coords. xy: current (if MLB down), zw: click
uniform vec3      iResolution;           // viewport resolution (in pixels)
uniform vec3      iChannelResolution[4]; // channel resolution (in pixels)
uniform int       iFrame;                // shader playback frame
uniform float     iTimeDelta;            // render time (in seconds)
uniform vec4      iDate;                 // (year, month, day, time in seconds)
// NOTE: Support 3D and cube samplers
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
