#version 440 core

layout (location = 0) in vec2 xyPos;
layout (location = 1) in vec2 uvTexCoord;

uniform uint branch_ID; 
uniform uint texture_layer;
uniform vec3 inColor;
uniform vec4 inRect;

// layout(location = 0) out vec3 vsColor;
layout (location = 0) out vec3 vsColor;
layout (location = 1) out vec2 vsTexCoord;

const vec3 color_predefined[6] = vec3[](
    vec3(1.0, 1.0, 1.0),
    vec3(1.0, 1.0, 0.0),
    vec3(0.0, 0.0, 1.0),
    vec3(0.0, 1.0, 1.0),
    vec3(1.0, 0.0, 1.0),
    vec3(0.0, 0.0, 0.0)
);

const vec2 square_point[4] = vec2[](
    vec2(inRect.x, inRect.y),
    vec2(inRect.x, inRect.w),
    vec2(inRect.z, inRect.w),
    vec2(inRect.z, inRect.y)
);

const vec2 test_point[4] = vec2[](
    vec2(0.5, 0.7),
    vec2(-0.5, -0.7),
    vec2(-0.4, 0.6),
    vec2(0.6, -0.4)
);

void main() { 
    if (branch_ID == 0) {
        gl_Position = vec4(xyPos , 0.0, 1.0);
        // gl_Position = vec4(test_point[gl_VertexID%4] , 0.0, 1.0);
    } else if (branch_ID == 1) {
        gl_Position = vec4(xyPos.x +inRect.z, xyPos.y+ inRect.w, 0.0, 1.0);
        // gl_Position = vec4(xyPos.x , xyPos.y , 0.0, 1.0);
        vsTexCoord = uvTexCoord;
    } else if (branch_ID == 2) {
        gl_Position = vec4(square_point[gl_VertexID] , 0.0, 1.0);
    } else {
        gl_Position = vec4(xyPos , 0.0, 1.0);
    }


    //vsColor = color_predefined[1]; 
    vsColor = inColor; 
  
}