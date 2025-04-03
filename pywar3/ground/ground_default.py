from OpenGL.GL import *

import numpy as np
import os
# if __name__ == "__main__":
#     from conf import *
# else:
#     from ground.conf import *

from .conf import * 
from .map_info import MapInfo
from .ground_mesh import GroundMesh_Cliff,GroundMesh_Frame,GroundMesh_Terrain,GroundMesh_Water

class GroundRenderEngine:
    # default_MVP = np.array([[1.0,  0.0,  0.0,  0.0],
    #                         [0.0,  1.0,  0.0,  0.0],
    #                         [0.0,  0.0,  1.0,  0.0],
    #                         [0.0,  0.0,  0.0,  1.0]], dtype='f4')
    default_MVP = np.array([
        [1.0711e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00],
        [0.0000e+00,  1.1839e+00,  5.6278e-01,  5.5919e-01],
        [0.0000e+00,  7.9861e-01, -8.3436e-01, -8.2903e-01],
        [0.0000e+00, -8.7167e-05,  1.6284e+03,  1.6500e+03]
    ],  dtype=np.float32)

    def __init__(self):
        mapw3e = MapInfo()
        self.map_width = mapw3e.width
        self.map_height = mapw3e.height
        self.map_bottom_left_x = mapw3e.center_offset_x
        self.map_bottom_left_y = mapw3e.center_offset_y
        self.map_z_list = np.array(
            mapw3e.ground_z_list).reshape((mapw3e.width, -1))

        # self.water_phase = 0
        self.mesh_args = {'water':{'phase':0}}
        self.mesh_group = {}
        for nm,cls in {'wireframe':GroundMesh_Frame, 
                   'terrain':GroundMesh_Terrain, 
                   'water':GroundMesh_Water, 
                   'cliff':GroundMesh_Cliff}.items():
            self.mesh_group[nm] = cls(mapw3e,
                                       os.path.join(GROUND_SHADER_FOLDER,f'{nm}.vert'),
                                       os.path.join(GROUND_SHADER_FOLDER,f'{nm}.frag'))
            
        self.MVP = self.default_MVP
        self.ubo_MVP = glGenBuffers(1)
        glBindBuffer(GL_UNIFORM_BUFFER, self.ubo_MVP)
        glBufferData(GL_UNIFORM_BUFFER, self.MVP.nbytes,
                     self.MVP, GL_STATIC_DRAW)
        glBindBufferBase(GL_UNIFORM_BUFFER, 0, self.ubo_MVP)

        corner_position_array = np.array(mapw3e.corner_point_array, dtype='f4')
        # corner_pos_buffer = glCreateBuffers(1)
        self.ubo_corner_pos = glGenBuffers(1)
        glBindBuffer(GL_UNIFORM_BUFFER, self.ubo_corner_pos)
        # glBufferData(GL_SHADER_STORAGE_BUFFER, corner_position_array.nbytes, corner_position_array, GL_STATIC_DRAW)
        # glNamedBufferStorage(cliff_level_buffer, width * height * sizeof(float), nullptr, GL_DYNAMIC_STORAGE_BIT)
        glBufferStorage(GL_UNIFORM_BUFFER, corner_position_array.nbytes,
                        corner_position_array, GL_DYNAMIC_STORAGE_BIT)
        glBindBufferBase(GL_UNIFORM_BUFFER, 1, self.ubo_corner_pos)

    def render(self, view=None, projection=None):
        for nm,mesh in self.mesh_group.items():
            mesh.render(**self.mesh_args.get(nm, {}))

    def destroy(self) -> None:
        for nm,mesh in self.mesh_group.items():
            mesh.destroy()

    def update_with_input(self, keys_state, window_state):
        MVP = window_state['mvp']
        glBindBuffer(GL_UNIFORM_BUFFER, self.ubo_MVP)
        glBufferData(GL_UNIFORM_BUFFER, MVP.nbytes, MVP, GL_STATIC_DRAW)
        # glBindBuffer(GL_UNIFORM_BUFFER, 0)
        self.mesh_args['water']['phase'] += window_state['frametime']
        # print(self.water_phase)

    def get_position_height(self, postion):
        
        pos_x, pos_y = postion[0], postion[1]
        quot_width, dx = divmod(pos_x - self.map_bottom_left_x, 128)
        quot_height, dy = divmod(pos_y - self.map_bottom_left_y, 128)
        ind_width = max(0, min(int(quot_width),self.map_z_list.shape[1]-2))
        ind_height = max(0, min(int(quot_height),self.map_z_list.shape[0]-2))

        b1 = self.map_z_list[ind_height][ind_width]
        b2 = self.map_z_list[ind_height][ind_width+1]
        t1 = self.map_z_list[ind_height+1][ind_width]
        t2 = self.map_z_list[ind_height+1][ind_width+1]
        bottom_z = (1-dx/128)*b1 + dx/128*b2
        top_z = (1-dx/128)*t1 + dx/128*t2
        pos_z = (1-dy/128)*bottom_z + dy/128*top_z
        return pos_z

if __name__ == "__main__":
    print(10 * "-", "debug", 10 * "-")

    from conf import *
    from sys import path
    path.append(ROOT)

    from main import App
    my_app = App()

    my_app.game_manager.fun_once_list = []
    # key_engine = GroundRenderEngine
    # key_engine = QuadBoardRenderEngine
    # my_app.game_manager.register_agent_engine(
    #         key_engine(my_app.game_manager))
    # my_app.game_manager.CreateDestructable("quadboard", 200, 200, 0)
    # my_app.game_manager.CreateDestructable(
    #           key_engine.agent_class_name, 200, 200, 0)

    my_app.run()
    my_app.quit()
