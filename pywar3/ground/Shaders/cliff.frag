#version 440 core

layout (binding = 0) uniform sampler2D cliff_texture;


layout (location = 0) in vec2 tex_Coord;
// layout (location = 0) in vec3 UV;

out vec4 color;

void main() {
	color = texture(cliff_texture, tex_Coord);
	//color = vec4(1.0,0.5,1.0,1.0);

}