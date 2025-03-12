#version 440 core

//layout (location = 0) in vec3 vsColor;
layout (location = 1) in vec2 vsTexCoord;

// uniform uint branch_ID; 
// uniform uint texture_layer;

layout (binding = 0) uniform sampler2D text_texture;

layout (location = 0) out vec4 FragColor;

void main() {
	if (11 == 11) {
		//FragColor = texture(cursor_textures, vec3(vsTexCoord,texture_layer));
    } else {
		// FragColor = vec4(1.0,1.0,1.0,1.0);
		//FragColor = vec4(vsColor,1.0);
    }
	FragColor = texture(text_texture, vsTexCoord) ;
	//FragColor = vec4(vsTexCoord,0.0,1.0);
}



