#version 440 core

layout (std140, binding = 0) uniform Matrices
{
    mat4 MVP;
};

layout (std140, binding = 1) uniform LineAttributes 
{
    vec4 point_position_list[];
};

layout(location = 0) uniform uint attr_offset; 

uniform mat4 view;
uniform mat4 projection;

layout(location = 0) out vec3 color;

const vec3 color_predefined[6] = vec3[](
    vec3(1.0, 1.0, 1.0),
    vec3(1.0, 1.0, 0.0),
    vec3(0.0, 0.0, 1.0),
    vec3(0.0, 1.0, 1.0),
    vec3(1.0, 0.0, 1.0),
    vec3(0.0, 0.0, 0.0)
);

struct line_attr {
    uint start_index;   
    uint index_stride;   
    uint line_color;    
};

layout(std430, binding = 2) buffer layoutName {
    line_attr line_attr_list[];
};

void main() { 
    // Access the line attributes using gl_InstanceID
    line_attr la = line_attr_list[gl_InstanceID + attr_offset];
    
    // Calculate the vertex position
    // vec3 point_position = point_position_list[la.start_index + la.index_stride * gl_VertexID].xyz / 2500.0;
    vec3 point_position = point_position_list[la.start_index + la.index_stride * gl_VertexID].xyz ;

    // Transform the vertex position using the MVP matrix
    // vec4 x_gl_Position = MVP * vec4(point_position.xy, point_position.z + 0.5, 1.0);
    // gl_Position = MVP * vec4(point_position.x / 2000.0, 0.0 , 0.0, 1.0);
    gl_Position = MVP * vec4(point_position.xy, point_position.z + 0.5, 1.0);

    // gl_Position = (projection * view) * vec4(point_position.xy, point_position.z + 0.5, 1.0);

    mat4 MVP_b = projection * view ;
    // gl_Position = MVP_b * vec4(point_position.xy, point_position.z + 0.5, 1.0);
    float elementa = MVP[1][2];
    float elementb = MVP_b[1][2];
    // gl_Position = vec4(point_position.xy /2500 + elementa - elementb, point_position.z  +0.5, 1.0);
    //gl_Position = vec4(point_position.xy /2500 + MVP_b[1][2], point_position.z  +0.5, 1.0);

    // Set the color based on the line attributes
    color = color_predefined[la.line_color % 6]; 
}

    vec3 linePositions[2][2] = vec3[][](
    vec3[](
        vec3(-0.5, 0.0, 0.0), // Start of line 1
        vec3(0.5, 0.0, 0.0)   // End of line 1
    ),
    vec3[](
        vec3(0.0, -0.5, 0.0), // Start of line 2
        vec3(0.0, 0.5, 0.0)   // End of line 2
    )
);

    // Set the position of the vertex based on the line index and vertex index
    //gl_Position = vec4(1.7*linePositions[lineIndex][vertexIndex], 1.0);
}