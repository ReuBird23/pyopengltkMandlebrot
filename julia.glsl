#version 330 core
uniform vec2 resolution;
uniform vec2 L_pan;
uniform vec2 R_pan;
uniform float scale;

out vec4 color;

vec2 f(vec2 c, vec2 z)
{
    return vec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + c;
}

vec3 HSV_to_RGB(vec3 col) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(col.xxx + K.xyz) * 6.0 - K.www);
    return col.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), col.y);
}

void main()
{
    vec2 c = L_pan;
    vec2 coord = (((gl_FragCoord.xy - resolution.xy/2)/resolution.x) * 2.0);
    vec2 z = coord / scale + R_pan;

    int max_iter = 128;
    int i = 0;
    while (i < max_iter && length(z) < 2.0)
    {
        z = f(c, z);
        ++i;
    }

    if (i == max_iter)
    {
        color = vec4(0.0, 0.0, 0.0, 1.0);
    } else {
        float t = float(i) / float(max_iter);
        color = vec4(HSV_to_RGB(vec3(t+0.6f, 1.0, 1.0)), 1.0);
    }
}
