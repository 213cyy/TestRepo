#version 440 core

// Interpolated values from the vertex shaders
in vec2 UV;
in vec3 color_Bright;
in vec2 bar_limit_X;

// Output data
out vec4 color;

// uniform sampler2D myTextureSampler;

const vec3 color_Background = vec3(0.1, 0.1, 0.1);

void main()
{
    if (UV.x < bar_limit_X.x || UV.x > bar_limit_X.y)
    {
        color = vec4(color_Background, 1.0);
    }
    else if (UV.y < 0.125 || UV.y > 0.875)
    {
        color = vec4(color_Background, 1.0);
    }
    else if (UV.y < 0.25)
    {
        // dark color
        color = vec4(0.36 * color_Bright, 1.0);
    }
    else if (UV.y > 0.75)
    {
        color = vec4(color_Bright, 1.0);
    }
    else
    {
        // normal color
        float d_coeff = (UV.x - bar_limit_X.x) * (bar_limit_X.y - UV.x);
        // color = vec4(0.59 * color_Bright, 1.0);
        color = vec4((0.40 + d_coeff) * color_Bright, 1.0);
    }
}
