#version 330 core

in vec4 fragTint;

// uniform vec3 object_color;
// uniform vec3 tint;
// uniform sampler2D imageTexture;

out vec4 color;


void main()
{
    // color = vec4(object_color, 1.0) * texture(imageTexture, fragmentTexCoord);
    // color = vec4(tint, 1) * baseTexture;

    color = fragTint;
}



