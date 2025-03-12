#version 440 core

layout (location = 0) in vec3 vsColor;

layout (location = 0) out vec4 FragColor;

void main() {
	// FragColor = vec4(1.0,1.0,1.0,1.0);
	FragColor = vec4(vsColor,1.0);
}