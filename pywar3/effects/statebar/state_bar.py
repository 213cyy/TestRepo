import numpy as np
import pyrr

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

if __name__ == "__main__":
    from conf import *
else:
    from effects.statebar.conf import *


class StateBar_Effect():
    effect_class_id = "lifebar"

    def __init__(self, engine, target_unit):
        self.render_engine = engine
        self.target_unit = target_unit

        target_height = 80
        self.anchor_position = target_unit.position + \
                            [0, 0, 1.2*target_height]

        self.life_percent = target_unit.health_val / target_unit.health_val_max
        self.scale = 1.2

    def update(self, frametime):
        target_height = 80
        self.anchor_position = self.target_unit.position + \
                              [0, 0, 1.2*target_height]

        self.life_percent = self.target_unit.health_val / self.target_unit.health_val_max

    def update_billboard(self, frametime):
        camera_pos = None
        self_to_camera = camera_pos - self.position
        self.eulers[2] = - \
            np.degrees(np.arctan2(-self_to_camera[1], self_to_camera[0]))
        dist2d = pyrr.vector.length(self_to_camera)
        self.eulers[1] = -np.degrees(np.arctan2(self_to_camera[2], dist2d))


class StateBar_Model:

    default_x = 0.0641
    default_y = 0.0126 * 8 / 6
    default_y = 0.0126 * 3
    def __init__(self):
        vert = (
            -1,  0.0,
            1,  0.0,
            -1,  1,
            1,  0.0,
            1,  1,
            -1,  1,
        )
        texc = (
            0, 0,
            1, 0,
            0, 1,
            1, 0,
            1, 1,
            0, 1
        )
        vert = np.array(vert).reshape((-1, 2))
        texc = np.array(texc).reshape((-1, 2))
        # vertices = np.hstack(([0.2,0.22,0.08]*vert, texc)).astype('f4')
        vertices = np.hstack((vert, texc)).astype('f4')

        self.vertex_count = int(len(vertices))

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes,
                     vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE,
                              16, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE,
                              16, ctypes.c_void_p(8))

        glBindVertexArray(0)

    def render(self):
        # glBindVertexArray(self.vao)
        # glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        # glDrawElements(GL_LINE_STRIP, self.indices_count,
        #                GL_UNSIGNED_INT,  ctypes.c_void_p(0))
        pass

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo, ))


class StateBarRenderEngine:
    default_MVP = np.array([
        [1.0711e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00],
        [0.0000e+00,  1.1839e+00,  5.6278e-01,  5.5919e-01],
        [0.0000e+00,  7.9861e-01, -8.3436e-01, -8.2903e-01],
        [0.0000e+00, -8.7167e-05,  1.6284e+03,  1.6500e+03]
    ],  dtype=np.float32)

    agent_class_name = 'statebar'

    def __init__(self, game_manager):
        self.game_manager = game_manager

        def create_shader(vertex_filepath: str, fragment_filepath: str) -> int:
            with open(vertex_filepath, 'r') as f:
                vertex_src = f.readlines()
            with open(fragment_filepath, 'r') as f:
                fragment_src = f.readlines()

            shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                    compileShader(fragment_src, GL_FRAGMENT_SHADER))

            return shader

        self.program = create_shader(
            SUB_ROOT+"bar.vert", SUB_ROOT+"bar.frag")
        glUseProgram(self.program)

        self.widget_list = []

        self.mesh_model = StateBar_Model()

        self.instanceVBO = glGenBuffers(1)
        # print(self.instanceVBO)
        glBindVertexArray(self.mesh_model.vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.instanceVBO)
        # glBufferData(GL_ARRAY_BUFFER, self.cubeTransforms.nbytes, self.cubeTransforms, GL_STATIC_DRAW)
        # layout(location = 0) in vec2 vertexOffset;
        # layout(location = 1) in vec2 vertexUV;
        # layout(location = 2) in vec3 anchorPosition;
        # layout(location = 3) in vec2 instanceSize;
        # layout(location = 4) in float colorPercentage;
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE,
                              24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE,
                              24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(4)
        glVertexAttribPointer(4, 1, GL_FLOAT, GL_FALSE,
                              24, ctypes.c_void_p(20))
        # 0: per shader call, 1: per instance
        glVertexAttribDivisor(2, 1)
        glVertexAttribDivisor(3, 1)
        glVertexAttribDivisor(4, 1)

    def create_agent(self,  target_unit):
        # entity
        agent = StateBar_Effect(self,  target_unit)
        self.widget_list.append(agent)
        return agent

    def render(self, window_state) -> None:

        glUseProgram(self.program)

        glBindVertexArray(self.mesh_model.vao)
        # print(glGetIntegerv(GL_ARRAY_BUFFER_BINDING))
        instanceAttr = []
        for k in self.widget_list:
            instanceAttr.extend(k.anchor_position)
            instanceAttr.extend([k.scale*self.mesh_model.default_x,self.mesh_model.default_y])
            instanceAttr.append(k.life_percent)

        instanceAttr = np.array(instanceAttr, dtype='f4')
        glBindBuffer(GL_ARRAY_BUFFER, self.instanceVBO)
        glBufferData(GL_ARRAY_BUFFER, instanceAttr.nbytes,
                     instanceAttr, GL_STATIC_DRAW)

        glDrawArraysInstanced(GL_TRIANGLES,
                              0, self.mesh_model.vertex_count, len(self.widget_list))

    def destroy(self) -> None:
        glDeleteProgram(self.program)
        self.mesh_model.destroy()


if __name__ == "__main__":
    print(10 * "-", "debug", 10 * "-")

    from conf import *
    from sys import path
    path.append(ROOT)

    from main import App
    my_app = App()
    # my_app.game_manager.fun_once_list = []

    # my_app.game_manager.register_agent_engine(
    #     QuadBoardRenderEnigine(my_app.game_manager))
    # my_app.game_manager.CreateDestructable("quadboard", 200, 200, 0)
    # my_app.game_manager.CreateDestructable("quadboard", 400, 200, 0, 2)
    # my_app.game_manager.CreateDestructable("quadboard", 400, 600, 0, 1.5)

    my_app.run()
    my_app.quit()
