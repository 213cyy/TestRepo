#version 440 core

layout (location = 0) in vec2 xyPos;
layout (location = 1) in vec2 uvTexCoord;

uniform uint branch_ID; 
uniform vec3 inColor;
uniform vec2 window_size;

//layout (location = 0) out vec3 vsColor;
layout (location = 1) out vec2 vsTexCoord;

const vec3 color_predefined[6] = vec3[](
    vec3(1.0, 1.0, 1.0),
    vec3(1.0, 1.0, 0.0),
    vec3(0.0, 0.0, 1.0),
    vec3(0.0, 1.0, 1.0),
    vec3(1.0, 0.0, 1.0),
    vec3(0.0, 0.0, 0.0)
);

const vec2 test_point[4] = vec2[](
    vec2(0.5, 0.7),
    vec2(-0.5, -0.7),
    vec2(-0.4, 0.6),
    vec2(0.6, -0.4)
);

void main() { 
    gl_Position = vec4(xyPos , 0.0, 1.0);
    vsTexCoord = uvTexCoord;

    //vsColor = color_predefined[1]; 
    //vsColor = inColor; 
}