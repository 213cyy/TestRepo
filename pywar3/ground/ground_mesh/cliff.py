from OpenGL.GL import *
from PIL import Image
import numpy as np
# try:
from .mesh import Mesh
try:
    from ..conf import *
except ImportError:
    from conf import *
class CliffTexture:

    # __slots__ = ("texture", "unit", "texture_type")

    def __init__(self):
        self.unit = 0
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                        GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        filepath = CLIFF_TEXTURE_FOLDER+"Cliff1.blp"
        with Image.open(filepath, mode="r") as img:
            image_width, image_height = img.size
            img = img.convert("RGBA")
            img_data = img.tobytes()
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width,
                         image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self) -> None:
        glActiveTexture(GL_TEXTURE0 + self.unit)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def destroy(self) -> None:
        glDeleteTextures(1, (self.texture,))


class Cliff(Mesh):

    def __init__(self, mapw3e, vert, frag) -> None:
        self.shader = self.create_shader(vert, frag)
        self.cliff_tex = CliffTexture()

        import importlib.util
        file_path = CLIFF_TEXTURE_FOLDER + 'cliff_data.py'
        # Load the module
        spec = importlib.util.spec_from_file_location('temp_module', file_path)
        module_data = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module_data)

        Vertices_16 = module_data.Vertices_16
        TVertices_16 = module_data.TVertices_16
        Triangles = module_data.Triangles

        v_16 = np.array(Vertices_16)
        # vert = np.array(Vertices_16, dtype=np.float32)
        vert = np.c_[v_16[:, 1], -v_16[:, 0], v_16[:, 2]].astype('f4')
        vert_uv = np.array(TVertices_16, dtype=np.float32)
        vertices = np.hstack((vert, vert_uv)).ravel()

        self.vertex_count = len(Vertices_16)
        self.indices_count = len(Triangles)

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

        self.ebo = glGenBuffers(1)
        indices = np.array(Triangles, dtype=np.uint32)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                     indices.nbytes, indices, GL_STATIC_DRAW)

        glBindVertexArray(0)

        cliff_tile_index = np.array(mapw3e.tile_cliff_inst, dtype='u4')
        self.instancecount = int(cliff_tile_index.size)

        self.water_index_buffer = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.water_index_buffer)
        glBufferStorage(GL_SHADER_STORAGE_BUFFER, cliff_tile_index.nbytes,
                        cliff_tile_index, GL_DYNAMIC_STORAGE_BIT)

        self.width_stride = mapw3e.width
        self.width_stride_location = 2

    def render(self) -> None:
        glUseProgram(self.shader)
        self.cliff_tex.use()
        # glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, self.corner_pos_buffer)
        glBindVertexArray(self.vao)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 2, self.water_index_buffer)
        glUniform1ui(self.width_stride_location, int(self.width_stride))

        # glDrawElements(GL_TRIANGLES, self.indices_count, GL_UNSIGNED_INT,ctypes.c_void_p(0))
        # glDrawElementsInstanced(GL_TRIANGLES, indices, GL_UNSIGNED_SHORT, nullptr, static_cast<int>(render_jobs.size()))

        glDrawElementsInstanced(GL_TRIANGLES, self.indices_count,
                                GL_UNSIGNED_INT, ctypes.c_void_p(0), self.instancecount)
        # glDrawArraysInstanced(GL_TRIANGLES, 0, 6, self.indices_count)

    def destroy(self) -> None:
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(2, (self.vbo, self.ebo))

