from OpenGL.GL import *
from PIL import Image
import numpy as np
from .mesh import Mesh

try:
    from ..conf import *
except ImportError:
    from conf import *

class WaterTexture:
    # Water textures
    lods = 8  # log2(128) + 1
    image_width = image_height = 128

    def __init__(self,):
        # glCreateTextures(GL_TEXTURE_2D_ARRAY, 1, &water_texture_array)
        # glTextureStorage3D(water_texture_array, self.lods, GL_RGBA8, 128, 128, WATER_TEXTURES_NUM)
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.texture)
        glTexStorage3D(GL_TEXTURE_2D_ARRAY, self.lods, GL_RGBA8,
                       128, 128, WATER_TEXTURES_NUM)
        glTexParameteri(GL_TEXTURE_2D_ARRAY,
                        GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D_ARRAY,
                        GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        for index in range(WATER_TEXTURES_NUM):
            filepath = WATER_INDEX_TO_FILENAME(index)
            with Image.open(filepath, mode="r") as image:
                # image_width,image_height = image.size # for texture size check
                img = image.convert("RGBA")
                glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0,
                                0, 0, index, 128, 128, 1,
                                GL_RGBA, GL_UNSIGNED_BYTE, img.tobytes())

        glGenerateMipmap(GL_TEXTURE_2D_ARRAY)

    def use(self) -> None:
        # glBindTextureUnit(GL_TEXTURE0 + unit, texture)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.texture)

    def destroy(self) -> None:
        glDeleteTextures(1, (self.texture,))


class Water(Mesh):
    def __init__(self, mapw3e, vert, frag) -> None:
        self.shader = self.create_shader(vert, frag)
        self.water_tex = WaterTexture()

        water_tile_index = np.array(mapw3e.tile_water_array, dtype='u4')
        self.instancecount = int(water_tile_index.size/6)

        self.water_index_buffer = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.water_index_buffer)
        glBufferStorage(GL_SHADER_STORAGE_BUFFER, water_tile_index.nbytes,
                        water_tile_index, GL_DYNAMIC_STORAGE_BIT)

        self.watertile_phase_buffer = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.watertile_phase_buffer)
        watertile_init_phase = np.random.randint(
            0, WATER_TEXTURES_NUM, self.instancecount, dtype='u4')
        glBufferStorage(GL_SHADER_STORAGE_BUFFER, watertile_init_phase.nbytes,
                        watertile_init_phase, GL_DYNAMIC_STORAGE_BIT)
        # glBufferData(GL_SHADER_STORAGE_BUFFER, line_attr_array.nbytes, line_attr_array, GL_STATIC_DRAW)

        # for glDrawArraysInstanced execution
        # To run glDrawArraysInstanced without encountering an exception,
        # we should provide a 'vao' if we haven't done so already
        self.vao_dummy = glGenVertexArrays(1)
        glBindVertexArray(self.vao_dummy)

        glBindVertexArray(0)
        self.water_phase_location = 2

    def render(self, phase=0):
        glUseProgram(self.shader)
        self.water_tex.use()
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 2, self.water_index_buffer)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 3,
                         self.watertile_phase_buffer)

        # glBindVertexArray(self.vao_dummy)
        water_phase_index = int(phase/67 % WATER_TEXTURES_NUM)
        # print(water_phase_index)

        glUniform1ui(self.water_phase_location, water_phase_index)
        glDrawArraysInstanced(GL_TRIANGLES, 0, 6, self.instancecount)

    def destroy(self):
        glDeleteProgram(self.shader)
        self.water_tex.destroy()
        glDeleteVertexArrays(1, (self.vao_dummy,))
        glDeleteBuffers(2, (self.water_index_buffer,
                        self.watertile_phase_buffer))
