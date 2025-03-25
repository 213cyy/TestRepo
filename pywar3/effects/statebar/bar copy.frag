#version 440 core

// Interpolated values from the vertex shaders
in vec2 UV;

// Output data
out vec4 color;

// uniform sampler2D myTextureSampler;

layout(location = 3) in float colorPercentage;

const vec3 color_100 = vec3(1.0, 1.0, 0.0);
const vec3 color_0 = vec3(1.0, 0.0, 0.0);
const vec3 color_Background = vec3(0.1, 0.1, 0.1);

void main(){
	vec3 color_Percent = mix(color_0,color_100,colorPercentage);
	vec3 color_Percent_bright = color_Percent * 0.2;

	// Output color = color of the texture at the specified UV
	color = vec4(color_100,1.0);
	
	// Hardcoded life level, should be in a separate texture.
	//if (UV.x < LifeLevel && UV.y > 0.3 && UV.y < 0.7 && UV.x > 0.04 )
		//color = vec4(0.2, 0.8, 0.2, 1.0); // Opaque green
}

