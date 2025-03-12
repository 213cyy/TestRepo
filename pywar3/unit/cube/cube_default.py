import numpy as np
import pyrr

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

if __name__ == "__main__":
    from conf import *
else:
    from unit.cube.conf import *


class UnitCube():
    unit_class_id = "cube"

    def __init__(self, player_id, position: list, eulers: list, color):
        self.player_id = player_id
        self.position = position
        self.eulers = eulers
        self.color = color

        self.mesh_model = UnitCube_Model(self)

        self.animate_time = 0
        self.animate_period = 5000

    def get_model_transform(self) -> np.ndarray:
        # model_transform = pyrr.matrix44.create_from_eulers(
        #     self.eulers[[2,0,1]], dtype=np.float32)
        model_transform = pyrr.matrix44.create_from_eulers(
            self.eulers, dtype=np.float32)

        return pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position), dtype=np.float32
            )
        )

    def update(self, frametime) -> None:
        self.eulers[1] += 6 * frametime / self.animate_period
        self.position[2] = 100*np.sin(self.animate_time)
        self.animate_time += 6.2831852 * frametime / self.animate_period

    def destroy(self):
        self.mesh_model.destroy()


class UnitCube_Model:
    def __init__(self, unit) -> None:
        self.unit = unit

        vertices = (
            -1.0, -1.0, 0.0,
            1.0, -1.0, 0.0,
            1.0,  1.0, 0.0,
            -1.0, -1.0, 2.0,
            1.0, -1.0, 2.0,
            1.0,  1.0, 2.0,
            -1.0, 1.0, 0.0,
            -1.0, -1.0, 0.0,
            -1.0, -1.0, 2.0,
            -1.0, 1.0, 0.0,
            1.0,  1.0, 0.0,
            1.0, 1.0, 2.0,
            -1.0, 1.0, 2.0
        )
        indices = (1, 4, 12, 6, 12, 3, 12, 5, 7, 4)
        vertices = 32*np.array(vertices, dtype=np.float32)
        self.vertex_count = 12
        indices = np.array(indices, dtype=np.uint32)
        self.indices_count = 10

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes,
                     vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                     indices.nbytes, indices, GL_STATIC_DRAW)

        glBindVertexArray(0)

    def render(self) -> None:
        glBindVertexArray(self.vao)

        # glDrawArrays(GL_LINE_STRIP, 0, self.vertex_count)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glDrawElements(GL_LINE_STRIP, self.indices_count,
                       GL_UNSIGNED_INT,  ctypes.c_void_p(0))

    def destroy(self) -> None:
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(2, (self.vbo, self.ebo))


class CubeRenderEnigine:
    default_MVP = np.array([
        [1.0711e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00],
        [0.0000e+00,  1.1839e+00,  5.6278e-01,  5.5919e-01],
        [0.0000e+00,  7.9861e-01, -8.3436e-01, -8.2903e-01],
        [0.0000e+00, -8.7167e-05,  1.6284e+03,  1.6500e+03]
    ],  dtype=np.float32)

    def __init__(self):
        def create_shader(vertex_filepath: str, fragment_filepath: str) -> int:
            with open(vertex_filepath, 'r') as f:
                vertex_src = f.readlines()
            with open(fragment_filepath, 'r') as f:
                fragment_src = f.readlines()

            shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                    compileShader(fragment_src, GL_FRAGMENT_SHADER))

            return shader

        self.program = create_shader(
            SUB_ROOT+"vertex.txt", SUB_ROOT+"fragment.txt")
        glUseProgram(self.program)

        self.projectMatrixLocation = glGetUniformLocation(
            self.program, "projection")
        self.modelMatrixLocation = glGetUniformLocation(self.program, "model")
        self.viewMatrixLocation = glGetUniformLocation(self.program, "view")
        self.colorLoc = glGetUniformLocation(self.program, "object_color")

        self.MVP = self.default_MVP
        self.ubo_MVP = glGenBuffers(1)
        glBindBuffer(GL_UNIFORM_BUFFER, self.ubo_MVP)
        glBufferData(GL_UNIFORM_BUFFER, self.MVP.nbytes,
                     self.MVP, GL_STATIC_DRAW)
        glBindBufferBase(GL_UNIFORM_BUFFER, 0, self.ubo_MVP)

        self.unit_group = set()

    def add_unit(self, unit):
        self.unit_group.add(unit)

    def render(self, window_state) -> None:
        MVP = window_state['mvp']
        glBindBuffer(GL_UNIFORM_BUFFER, self.ubo_MVP)
        glBufferData(GL_UNIFORM_BUFFER, MVP.nbytes, MVP, GL_STATIC_DRAW)
        glUseProgram(self.program)
        for k in self.unit_group:
            glUniformMatrix4fv(self.modelMatrixLocation,
                               1, GL_FALSE, k.get_model_transform())
            glUniform3fv(self.colorLoc, 1, k.color)
            k.mesh_model.render()

    def destroy(self) -> None:
        glDeleteProgram(self.program)
        for k in self.unit_group:
            k.destroy()
