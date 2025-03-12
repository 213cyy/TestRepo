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
    point_attr point_attr_list[];
};

const vec2 coord_predefined[6] = vec2[](
    vec2(0.0, 0.0 ),
    vec2(1.0, 0.0 ),
    vec2(0.0, 1.0 ),
    vec2(1.0, 0.0 ),
    vec2(1.0, 1.0 ),
    vec2(0.0, 1.0 )
);

layout(std430, binding = 2) buffer layoutName {
    uint ground_index_list[];
};

layout(std430, binding = 3) buffer layoutName2 {
    uvec4 groundtile_inst_list[];
};


layout(location = 0) out flat uvec4 tex_Index;
layout(location = 1) out vec2 tex_Coord_UV;

void main() { 
	uint g_index = ground_index_list[gl_InstanceID * 6 + gl_VertexID];
	point_attr p_attr = point_attr_list[g_index];
	vec4 pos = p_attr.point_position;

    // Transform the vertex position using the MVP matrix
    gl_Position = MVP * vec4(pos.xyz, 1.0);

    tex_Coord_UV = coord_predefined[gl_VertexID];
	tex_Index = groundtile_inst_list[gl_InstanceID];

 }