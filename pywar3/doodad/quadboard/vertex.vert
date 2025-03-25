#version 440 core

layout (std140, binding = 0) uniform Matrices
{
    mat4 MVP;
};

layout (location = 0) in vec3 vertexPos;
layout (location = 1) in vec3 instanceOffset;
layout (location = 2) in vec3 instanceColor;
layout (location = 3) in float instanceScale;

out vec4 fragTint;


void main()
{
    gl_Position = MVP * vec4(instanceScale*vertexPos+instanceOffset, 1.0);
    fragTint = vec4(instanceColor, 1.0);
}


