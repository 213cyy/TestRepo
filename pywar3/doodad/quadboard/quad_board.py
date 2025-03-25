import numpy as np
import pyrr

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

if __name__ == "__main__":
    from conf import *
else:
    from doodad.quadboard.conf import *


class Board_Doodad():
    doodad_class_id = "board_doodad"

    # (position,eulers,scale,variation)
    def __init__(self, engine, position, eulers, scale, variation):
        self.render_engine = engine
        self.position = position
        self.eulers = eulers
        self.scale = scale
        self.variation = variation

        self.velocity = 0.1
        d_xy = np.random.rand(2)
        speed = self.velocity * d_xy / np.linalg.norm(d_xy)
        self.d_position = np.hstack((speed, 0))

        self.color = 0.5*np.random.rand(3)+0.5
        self.d_color = 0.1 * np.random.rand(3)

        self.animate_time = 0
        self.animate_period = 5000

    def get_model_transform(self):
        model_transform = pyrr.matrix44.create_from_eulers(
            self.eulers, dtype=np.float32)

        return pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position), dtype=np.float32
            )
        )

    def update(self, frametime):
        self.position += self.velocity * frametime * self.d_position
        z = self.render_engine.game_manager.window_info.ground.\
                get_position_height( self.position)
        self.position[2] = z
        self.animate_time += frametime
        if self.animate_time > self.animate_period:
            self.animate_time = 0
            dest_xy = 3000*(np.random.rand(2)-0.5)
            d_xy = dest_xy - self.position[:2]
            speed = d_xy / np.linalg.norm(d_xy)
            self.d_position = np.hstack((speed, 0))

        color = self.color + 0.0005 * frametime * self.d_color
        # print(self.color,color)
        if (sum(color) > 1.0) and all(0.1 < color ) and all(color < 0.9):
            self.color = color
        else:
            self.color = np.clip(color, 0.1, 0.9)
            color_target = 0.4*np.random.rand(3)+0.4
            d_color = (color_target-color)
            self.d_color = d_color / np.linalg.norm(d_color)


class Board_Model:
    def __init__(self):
        vertices = (
            -80,  0.0, 0,
            80,  0.0, 0,
            -80,  0.0, 100,
            80,  0.0, 0,
            80,  0.0, 100,
            -80,  0.0, 100,
        )

        self.vertex_count = len(vertices)//3
        self.vertices = np.array(vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes,
                     self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

        glBindVertexArray(0)

    def render(self):
        # glBindVertexArray(self.vao)
        # glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        pass

    def destroy(self) -> None:
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))


class QuadBoardRenderEngine:
    default_MVP = np.array([
        [1.0711e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00],
        [0.0000e+00,  1.1839e+00,  5.6278e-01,  5.5919e-01],
        [0.0000e+00,  7.9861e-01, -8.3436e-01, -8.2903e-01],
        [0.0000e+00, -8.7167e-05,  1.6284e+03,  1.6500e+03]
    ],  dtype=np.float32)

    agent_class_name = 'quadboard'

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
            SUB_ROOT+"vertex.vert", SUB_ROOT+"fragment.frag")
        glUseProgram(self.program)

        # self.projectMatrixLocation = glGetUniformLocation(
        #     self.program, "projection")
        # self.modelMatrixLocation = glGetUniformLocation(self.program, "model")
        # self.viewMatrixLocation = glGetUniformLocation(self.program, "view")
        # self.colorLoc = glGetUniformLocation(self.program, "object_color")

        self.MVP = self.default_MVP
        self.ubo_MVP = glGenBuffers(1)
        glBindBuffer(GL_UNIFORM_BUFFER, self.ubo_MVP)
        glBufferData(GL_UNIFORM_BUFFER, self.MVP.nbytes,
                     self.MVP, GL_STATIC_DRAW)
        glBindBufferBase(GL_UNIFORM_BUFFER, 0, self.ubo_MVP)

        self.widget_list = []

        self.mesh_model = Board_Model()

        self.instanceVBO = glGenBuffers(1)
        # print(self.instanceVBO)
        glBindVertexArray(self.mesh_model.vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.instanceVBO)
        # glBufferData(GL_ARRAY_BUFFER, self.cubeTransforms.nbytes, self.cubeTransforms, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE,
                              28, ctypes.c_void_p(0))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE,
                              28, ctypes.c_void_p(12))
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 1, GL_FLOAT, GL_FALSE,
                              28, ctypes.c_void_p(24))
        # 0: per shader call, 1: per instance
        glVertexAttribDivisor(1, 1)
        glVertexAttribDivisor(2, 1)
        glVertexAttribDivisor(3, 1)

    def create_agent(self, position, eulers, scale, variation):
        # entity
        agent = Board_Doodad(self, position, eulers, scale, variation)
        self.widget_list.append(agent)
        return agent

    def render(self, window_state) -> None:
        MVP = window_state['mvp']
        glBindBuffer(GL_UNIFORM_BUFFER, self.ubo_MVP)
        glBufferData(GL_UNIFORM_BUFFER, MVP.nbytes, MVP, GL_STATIC_DRAW)

        glUseProgram(self.program)

        glBindVertexArray(self.mesh_model.vao)
        # print(glGetIntegerv(GL_ARRAY_BUFFER_BINDING))
        instanceAttr = []
        for k in self.widget_list:
            instanceAttr.extend(k.position)
            instanceAttr.extend(k.color)
            instanceAttr.append(k.scale)
        instanceAttr = np.array(instanceAttr, dtype='f4')
        glBindBuffer(GL_ARRAY_BUFFER, self.instanceVBO)
        glBufferData(GL_ARRAY_BUFFER, instanceAttr.nbytes,
                     instanceAttr, GL_STATIC_DRAW)
        glDrawArraysInstanced(
            GL_TRIANGLES, 0, self.mesh_model.vertex_count, len(self.widget_list))

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
    my_app.game_manager.fun_once_list = []

    my_app.game_manager.register_agent_engine(
        QuadBoardRenderEngine(my_app.game_manager))
    my_app.game_manager.CreateDestructable("quadboard", 200, 200, 0)
    my_app.game_manager.CreateDestructable("quadboard", 400, 200, 0, 2)
    my_app.game_manager.CreateDestructable("quadboard", 400, 600, 0, 1.5)

    my_app.run()
    my_app.quit()
