import numpy as np
import pyrr
from PIL import Image

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

if __name__ == "__main__":
    from conf import *
    from sys import path
    path.append(AGENT_ROOT)
    from unit_default import *

else:
    from units.nounit.conf import *
    from units.unit_default import *


class UnitNone(UnitDefault):
    unit_class_id = "none"

    def __init__(self, engine, player_id, position, eulers, color):
        super().__init__(engine, player_id, position, eulers, color)
        # self.render_engine = engine
        # self.player_id = player_id
        # self.position = position
        # self.eulers = eulers
        # self.color = color

        self.pos_origin_z = position[2]
        self.pos_origin_z = 100

        self.mesh_model = UnitNone_Model(self)

        self.animate_time = 0
        self.animate_period = 5000

    def get_model_transform(self) -> np.ndarray:
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
        self.animate_time += 6.2831852 * frametime / self.animate_period
        self.position[0] += 3*np.sin(self.animate_time)
        self.position[1] += 3*np.cos(self.animate_time)
        z = self.render_engine.game_manager.window_info.ground.\
            get_position_height(self.position)
        self.position[2] = self.pos_origin_z+z

        self.health_val = 0.5*self.health_val_max * \
            ( 1 + 0.9*np.sin(0.5*self.animate_time) )

    def destroy(self):
        self.mesh_model.destroy()


class UnitNone_Model:
    def __init__(self, unit) -> None:
        self.unit = unit
        self.texture = UnitNone_Texture()
        vertices = (
            -1.0, -1.0,  0.0,  0.0, 0.0,
            1.0, -1.0,  0.0,  1.0, 0.0,
            1.0,  1.0,  0.0,  1.0, 1.0,
            1.0,  1.0,  0.0,  1.0, 1.0,
            -1.0,  1.0,  0.0,  0.0, 1.0,
            -1.0, -1.0,  0.0,  0.0, 0.0,

            -1.0, -1.0,  2.0,  10.0, 10.0,
            1.0, -1.0,  2.0,  10.0, 10.0,
            1.0,  1.0,  2.0,  10.0, 10.0,
            1.0,  1.0,  2.0,  1.0, 1.0,
            -1.0,  1.0,  2.0,  0.0, 1.0,
            -1.0, -1.0,  2.0,  0.0, 0.0,

            -1.0,  1.0,  2.0,  1.0, 0.0,
            -1.0,  1.0,  0.0,  1.0, 1.0,
            -1.0, -1.0,  0.0,  0.0, 1.0,
            -1.0, -1.0,  0.0,  0.0, 1.0,
            -1.0, -1.0,  2.0,  0.0, 0.0,
            -1.0,  1.0,  2.0,  1.0, 0.0,

            1.0,  1.0,  2.0,  1.0, 0.0,
            1.0,  1.0,  0.0,  1.0, 1.0,
            1.0, -1.0,  0.0,  0.0, 1.0,
            1.0, -1.0,  0.0,  0.0, 1.0,
            1.0, -1.0,  2.0,  0.0, 0.0,
            1.0,  1.0,  2.0,  1.0, 0.0,

            -1.0, -1.0,  0.0,  0.0, 1.0,
            1.0, -1.0,  0.0,  1.0, 1.0,
            1.0, -1.0,  2.0,  1.0, 0.0,
            1.0, -1.0,  2.0,  1.0, 0.0,
            -1.0, -1.0,  2.0,  0.0, 0.0,
            -1.0, -1.0,  0.0,  0.0, 1.0,

            -1.0,  1.0,  0.0,  0.0, 1.0,
            1.0,  1.0,  0.0,  1.0, 1.0,
            1.0,  1.0,  2.0,  1.0, 0.0,
            1.0,  1.0,  2.0,  1.0, 0.0,
            -1.0,  1.0,  2.0,  0.0, 0.0,
            -1.0,  1.0,  0.0,  0.0, 1.0
        )
        n = 6*6
        v = (n * [40, 40, 40, 1, 1])*np.array(vertices)

        vertices = v.astype(np.float32)
        self.vertex_count = n

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes,
                     vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE,
                              20, ctypes.c_void_p(12))
        glBindVertexArray(0)

    def render(self) -> None:
        self.texture.use()
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self) -> None:
        self.texture.destroy()
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo, ))


class UnitNone_Texture:

    def __init__(self, unit=0):
        self.unit = unit
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                        GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        filepath = SUB_ROOT+"awesomeface.png"
        with Image.open(filepath, mode="r") as img:
            image_width, image_height = img.size
            img = img.convert("RGBA")
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width,
                         image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self) -> None:
        glActiveTexture(GL_TEXTURE0 + self.unit)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def destroy(self) -> None:
        glDeleteTextures(1, (self.texture,))


class CubeNoneRenderEngine:
    default_MVP = np.array([
        [1.0711e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00],
        [0.0000e+00,  1.1839e+00,  5.6278e-01,  5.5919e-01],
        [0.0000e+00,  7.9861e-01, -8.3436e-01, -8.2903e-01],
        [0.0000e+00, -8.7167e-05,  1.6284e+03,  1.6500e+03]
    ],  dtype=np.float32)

    agent_class_name = "none_unit"

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

    def create_agent(self, player_id, position, eulers, color):
        # entity
        agent = UnitNone(self, player_id, position, eulers, color)
        self.unit_group.add(agent)
        return agent

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


if __name__ == "__main__":
    print(10 * "-", "debug", 10 * "-")

    from conf import *
    from sys import path
    path.append(ROOT)

    from main import App
    my_app = App()
    my_app.game_manager.fun_once_list = []

    my_app.game_manager.register_agent_engine(
        CubeNoneRenderEngine(my_app.game_manager))
    my_app.game_manager.CreateUnit(4, "none_unit", -400, 200, 0)
    my_app.game_manager.CreateUnit(5, "none_unit", 200, -500, 50)
    my_app.game_manager.CreateUnit(6, "none_unit", -600, -600, 100)

    my_app.run()
    my_app.quit()
