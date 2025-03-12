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

layout (std430, binding = 2) buffer layoutName {
    uint water_index_list[];
};

layout (std430, binding = 3) buffer layoutName2 {
    uint watertile_phase_list[];
};

layout (location = 2) uniform uint water_phase;

const uint WATER_TEXTURES_NUM = 45;

layout (location = 0) out vec4 frag_color;
layout (location = 1) out vec3 tex_coord;

void main() { 
	uint w_index = water_index_list[gl_InstanceID * 6 + gl_VertexID];
	point_attr p_attr = point_attr_list[w_index];
	vec4 pos = p_attr.point_position;

    // Transform the vertex position using the MVP matrix
    gl_Position = MVP * vec4(pos.xyw, 1.0);
	frag_color = p_attr.point_color;
    uint tex_index = (water_phase + watertile_phase_list[gl_InstanceID]) % WATER_TEXTURES_NUM;
	tex_coord = vec3(coord_predefined[gl_VertexID], tex_index );

 }