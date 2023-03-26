#version 330

#define KERNEL_SIZE 11
#define MY_KERNEL (0.03582200398765452, 0.058789717526710104, 0.0864248760489264, 0.11380609461934069, 0.13423950363098489, 0.14183560837276687, 0.13423950363098489, 0.11380609461934069, 0.0864248760489264, 0.058789717526710104, 0.03582200398765452)

uniform sampler2D texture0;
uniform vec2 target_size;

in vec2 v_uv;
out vec4 outColor;

// https://observablehq.com/@jobleonard/gaussian-kernel-calculater
const int KERNEL_RANGE = (KERNEL_SIZE - 1) / 2;
const float KERNEL[KERNEL_SIZE] = float[KERNEL_SIZE]MY_KERNEL;

void main() {
    vec4 col = vec4(0.0);
    vec2 uv_step = vec2(1.0) / target_size;
    for (int i = 0; i < KERNEL_SIZE; i++) {
        col += texture(texture0, v_uv + vec2(uv_step.x * float(i - KERNEL_RANGE), 0.0)) * KERNEL[i];
    }
    outColor = vec4(col.rgb, 1.0);
}
