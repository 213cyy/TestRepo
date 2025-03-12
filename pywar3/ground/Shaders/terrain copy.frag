#version 440 core

layout (binding = 0) uniform sampler2DArray texSamples[16];
layout (binding = 1) uniform sampler2DArray sample1;
layout (binding = 2) uniform sampler2DArray sample2;
layout (binding = 3) uniform sampler2DArray sample3;
layout (binding = 4) uniform sampler2DArray sample4;
layout (binding = 5) uniform sampler2DArray sample5;
layout (binding = 6) uniform sampler2DArray sample6;
layout (binding = 7) uniform sampler2DArray sample7;
layout (binding = 8) uniform sampler2DArray sample8;
layout (binding = 9) uniform sampler2DArray sample9;
layout (binding = 10) uniform sampler2DArray sample10;
layout (binding = 11) uniform sampler2DArray sample11;
layout (binding = 12) uniform sampler2DArray sample12;
layout (binding = 13) uniform sampler2DArray sample13;
layout (binding = 14) uniform sampler2DArray sample14;
layout (binding = 15) uniform sampler2DArray sample15;
layout (binding = 16) uniform sampler2DArray sample0;


layout(location = 0) in flat uvec4 tex_Index;
layout(location = 1) in vec2 tex_Coord_UV;

// layout (location = 0) in vec2 UV;
// layout (location = 1) in flat uvec4 texture_indices;

layout (location = 0) out vec4 color;

vec4 get_fragment(uint id, vec3 uv) {
	vec2 dx = dFdx(uv.xy);
	vec2 dy = dFdy(uv.xy);

	switch(id) {
		case 0:
			return textureGrad(sample0, uv, dx, dy);
		case 1:
			return textureGrad(sample1, uv, dx, dy);
		case 2:
			return textureGrad(sample2, uv, dx, dy);
		case 3:
			return textureGrad(sample3, uv, dx, dy);
		case 4:
			return textureGrad(sample4, uv, dx, dy);
		case 5:
			return textureGrad(sample5, uv, dx, dy);
		case 6:
			return textureGrad(sample6, uv, dx, dy);
		case 7:
			return textureGrad(sample7, uv, dx, dy);
		case 8:
			return textureGrad(sample8, uv, dx, dy);
		case 9:
			return textureGrad(sample9, uv, dx, dy);
		case 10:
			return textureGrad(sample10, uv, dx, dy);
		case 11:
			return textureGrad(sample11, uv, dx, dy);
		case 12:
			return textureGrad(sample12, uv, dx, dy);
		case 13:
			return textureGrad(sample13, uv, dx, dy);
		case 14:
			return textureGrad(sample14, uv, dx, dy);
		case 15:
			return textureGrad(sample15, uv, dx, dy);
		case 16:
			return vec4(0, 0, 0, 0);
	}
}


void main() {
	// color = get_fragment(texture_indices.a & 31, vec3(UV, texture_indices.a >> 5));
	// color = mix(get_fragment(texture_indices.b & 31, vec3(UV, texture_indices.b >> 5)), color, color.a);
	// color = mix(get_fragment(texture_indices.g & 31, vec3(UV, texture_indices.g >> 5)), color, color.a);
	// color = mix(get_fragment(texture_indices.r & 31, vec3(UV, texture_indices.r >> 5)), color, color.a);

	color = texture(texSamples[tex_Index.r & 31], vec3(tex_Coord_UV, tex_Index.r >> 5));
	color = mix( texture( texSamples[tex_Index.g & 31], vec3(tex_Coord_UV, tex_Index.g >> 5) ), color, color.a );
	color = mix( texture( texSamples[tex_Index.b & 31], vec3(tex_Coord_UV, tex_Index.b >> 5) ), color, color.a );
	color = mix( texture( texSamples[tex_Index.a & 31], vec3(tex_Coord_UV, tex_Index.a >> 5) ), color, color.a );


	color = vec4(0.4,1.0,0.5,1.0);
	// color = texture(texSamples[tex_Index.r & 31], vec3(tex_Coord_UV, tex_Index.r >> 5));
	// color = mix( texture( texSamples[tex_Index.g & 31], vec3(tex_Coord_UV, tex_Index.g >> 5) ), color, color.a );
	// color = mix( texture( texSamples[tex_Index.b & 31], vec3(tex_Coord_UV, tex_Index.b >> 5) ), color, color.a );
	// color = mix( texture( texSamples[tex_Index.a & 31], vec3(tex_Coord_UV, tex_Index.a >> 5) ), color, color.a );
	color = get_fragment( tex_Index.r , tex_Coord_UV );
	// color = mix( get_fragment( tex_Index.g , tex_Coord_UV ), color, color.a );
	// color = mix( get_fragment( tex_Index.b , tex_Coord_UV ), color, color.a );
	// color = mix( get_fragment( tex_Index.a , tex_Coord_UV ), color, color.a );
}