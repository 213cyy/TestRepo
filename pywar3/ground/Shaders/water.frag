#version 440 core

layout (binding = 0) uniform sampler2DArray water_textures;



layout(location = 0) in vec4 frag_color;
layout(location = 1) in vec3 tex_coord;

out vec4 outColor;

void main() {
	//uint tex_index = water_phase % WATER_TEXTURES_NUM;
	outColor = texture(water_textures, tex_coord) * frag_color;
	// outColor = frag_color;
	// outColor = vec4(0.5,0.6,0.7,1.0);
	// outColor = vec4(tex_coord,0.7,1.0);
}