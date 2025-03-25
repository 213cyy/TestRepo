#version 440 core

layout(std140, binding = 0) uniform Matrices
{
    mat4 MVP;
};

layout(location = 0) in vec2 vertexOffset;
layout(location = 1) in vec2 vertexUV;
layout(location = 2) in vec3 anchorPosition;
layout(location = 3) in vec2 instanceSize;
layout(location = 4) in float healthPercentage;

out vec2 UV;
out vec3 color_Bright;
out vec2 bar_limit_X;

const vec3 pos_predefined[6] = vec3[](
    vec3(0.0, 0.0, 0.0),
    vec3(0.5, 0.0, 0.0),
    vec3(0.0, 0.5, 0.0),
    vec3(0.5, 0.0, 0.0),
    vec3(0.5, 0.25, 0.0),
    vec3(0.25, 0.25, 0.0));

void main()
{
    vec4 anchor_center = MVP * vec4(anchorPosition, 1.0);
    vec2 pos_XY = anchor_center.xy / anchor_center.w;

    //vec3 temp_Pos = pos_predefined[gl_VertexID];
    //gl_Position = vec4( temp_Pos.x+pos_XY.x, temp_Pos.y+pos_XY.y, 0.0, 1.0);

    vec2 offset_XY = vertexOffset * instanceSize;

    gl_Position = vec4(pos_XY + offset_XY, 0.0, 1.0);

    UV = vertexUV;

    float hhh = clamp(healthPercentage, 0.0, 1.0);
    color_Bright = vec3(1.0 - pow(hhh, 3.2), 1.0 - pow(1.0 - hhh, 3.2), 0.0);

    float temp_a = 0.125 * instanceSize.y / 2.0 / instanceSize.x;
    bar_limit_X = vec2(temp_a, temp_a + (1 - 2 * temp_a) * healthPercentage);
}
