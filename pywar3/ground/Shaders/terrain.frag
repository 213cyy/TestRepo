#version 440 core

layout (binding = 0) uniform sampler2DArray sample0;
layout (binding = 1) uniform sampler2DArray sample1;
layout (binding = 2) uniform sampler2DArray sample2;
layout (binding = 3) uniform sampler2DArray sample3;
layout (binding = 4) uniform sampler2DArray sample4;
layout (binding = 5) uniform sampler2DArray sample5;
layout (binding = 6) uniform sampler2DArray sample6;
layout (binding = 7) uniform sampler2DArray sample7;
layout (binding = 8) uniform sampler2DArray sample8;
layout (binding = 9) uniform sampler2DArray sample9;


layout(location = 0) in flat uvec4 tex_Index;
layout(location = 1) in vec2 tex_Coord_UV;

// layout (location = 0) in vec2 UV;
// layout (location = 1) in flat uvec4 texture_indices;

layout (location = 0) out vec4 color;

vec4 get_fragment(uint ind, vec2 uv) {
	uint id = ind & 31;
	uint layer = ind >> 5;

	switch(id) {
		case 0:
			return texture(sample0, vec3(uv, layer) );
		case 1:
			return texture(sample1, vec3(uv, layer) );
		case 2:
			return texture(sample2, vec3(uv, layer) );
		case 3:
			return texture(sample3, vec3(uv, layer) );
		case 4:
			return texture(sample4, vec3(uv, layer) );
		case 5:
			return texture(sample5, vec3(uv, layer) );
		case 6:
			return texture(sample6, vec3(uv, layer) );
		case 7:
			return texture(sample7, vec3(uv, layer) );
		case 8:
			return texture(sample8, vec3(uv, layer) );
		case 9:
			return texture(sample9, vec3(uv, layer) );
	}
	return vec4(0, 0, 0, 0);
}

void main() {
	//color = vec4(0.4,1.0,0.5,1.0);
	color = get_fragment( tex_Index.a , tex_Coord_UV );
	color = mix( get_fragment( tex_Index.b , tex_Coord_UV ), color, color.a );
	color = mix( get_fragment( tex_Index.g , tex_Coord_UV ), color, color.a );
	color = mix( get_fragment( tex_Index.r , tex_Coord_UV ), color, color.a );
}