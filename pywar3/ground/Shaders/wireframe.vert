#version 440 core

layout (std140, binding = 0) uniform Matrices
{
    mat4 MVP;
};

struct point_attr {
    vec4 point_position;
    vec4 point_color;  
};

layout (std140, binding = 1) uniform CornerAttributes 
{
    // vec4 point_position_list[];
    point_attr point_attr_list[];
};

layout(location = 0) uniform uint attr_offset; 

layout(location = 0) out vec3 vsColor;

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
    //line_attr la = line_attr_list[gl_InstanceID + attr_offset];
    //vec3 point_position = point_position_list[la.start_index + la.index_stride * gl_VertexID].xyz ;
    //gl_Position = MVP * vec4(point_position.xy, point_position.z + 10.0, 1.0);




    
    // Calculate the vertex position
    line_attr la = line_attr_list[gl_InstanceID + attr_offset];
    // uint a = attr_offset;
    // line_attr la = line_attr_list[0];
    point_attr point_attribute = point_attr_list[la.start_index + la.index_stride * gl_VertexID] ;
    //point_attr point_attribute = point_attr_list[gl_VertexID] ;
    vec4 point_pos = point_attribute.point_position ;
    gl_Position = MVP * vec4(point_pos.xy, point_pos.z + 10.0, 1.0);
    // gl_Position = MVP * vec4(gl_VertexID*100, 0.0,point_attribute.point_color.x, 1.0);

    // Set the color based on the line attributes
    vsColor = color_predefined[la.line_color % 6]; 
}