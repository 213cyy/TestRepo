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


layout (location = 0) in vec3 vPosition;
layout (location = 1) in vec2 vUV;
//layout (location = 2) in vec3 vNormal;
//layout (location = 3) in vec4 vOffset;

layout (location = 0) out vec2 tex_Coord;
// layout (location = 0) out vec3 UV;


layout(std430, binding = 2) buffer layoutName1 {
    uint BL_point_index[];
};

const vec3 test_points[6] = vec3[](
    vec3(200.0, 200.0, 200.0),
    vec3(200.0, 200.0, 0.0),
    vec3(0.0, 0.0, 200.0),
    vec3(0.0, 200.0, 200.0),
    vec3(200.0, 0.0, 200.0),
    vec3(0.0, 0.0, 0.0)
);

layout (location = 2) uniform uint width_stride;

void main() {
	// WC3 cliff meshes seem to be rotated by 90 degrees so we unrotate
	// const vec3 rotated_world_position = vec3(vPosition.y, -vPosition.x, vPosition.z) / 128.f + vOffset.xyz;

	// const ivec2 height_pos = ivec2(rotated_world_position.xy);
	// const float height = cliff_levels[height_pos.y * map_size.x + height_pos.x];

	// const ivec3 off = ivec3(1, 1, 0);

	// const float hL = cliff_levels[height_pos.y * map_size.x + max(height_pos.x - 1, 0)];
	// const float hR = cliff_levels[height_pos.y * map_size.x + min(height_pos.x + 1, map_size.x)];
	// const float hD = cliff_levels[max(height_pos.y - 1, 0) * map_size.x + height_pos.x];
	// const float hU = cliff_levels[min(height_pos.y + 1, map_size.y) * map_size.x + height_pos.x];
	// const vec3 terrain_normal = normalize(vec3(hL - hR, hD - hU, 2.0));

	// Get the 4 closest heights in the height map.
	uint bottomLeft_index = BL_point_index[gl_InstanceID];
	vec4 bottomLeft_pos = point_attr_list[bottomLeft_index].point_position;
	vec4 bottomRight_pos = point_attr_list[bottomLeft_index+1].point_position;
	vec4 topLeft_pos = point_attr_list[bottomLeft_index+width_stride].point_position;
	vec4 topRight_pos = point_attr_list[bottomLeft_index+width_stride+1].point_position;


	// Do a bilinear interpolation between the heights to get the final value.
	float bottom = mix(bottomRight_pos.z, bottomLeft_pos.z, 1-vPosition.x / 128.0);
	float top = mix(topRight_pos.z, topLeft_pos.z, 1-vPosition.x / 128.0);
	float height = mix(bottom, top, vPosition.y / 128.0);

	float cliff_z = min( min(bottomRight_pos.z, bottomLeft_pos.z) , min(topRight_pos.z, topLeft_pos.z) );
	float coeff =  height - cliff_z - vPosition.y;
	gl_Position = MVP * vec4( vPosition.xy + bottomLeft_pos.xy , cliff_z + vPosition.z + height , 1.0);
	gl_Position = MVP * vec4(vPosition.xy+bottomLeft_pos.xy, cliff_z + coeff + vPosition.z  , 1.0);
	// gl_Position = MVP * vec4(test_points[gl_VertexID], 1.0);
	// gl_Position = vec4(test_points[gl_VertexID], 1.0);


	tex_Coord = vUV;


}