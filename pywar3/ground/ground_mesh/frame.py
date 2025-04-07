from OpenGL.GL import *
from PIL import Image
import numpy as np
from .mesh import Mesh

try:
    from ..conf import *
except ImportError:
    from conf import *

class Frame(Mesh):
    def __init__(self, mapw3e, vert, frag) -> None:
        self.shader = self.create_shader(vert, frag)

        self.width_n = width_n = mapw3e.width
        self.height_n = height_n = mapw3e.height
        print('mapw3e:',mapw3e.width, mapw3e.height)
        row_start = list(range(0, height_n*width_n, width_n))
        row_stride = [1] * height_n
        row_color = [1, 0, 0, 0] * (height_n//4) + [1]
        col_start = list(range(0, width_n))
        col_stride = [width_n] * width_n
        col_color = [1, 0, 0, 0] * (width_n//4) + [1]

        temp_array = np.dstack((row_start+col_start,
                                row_stride + col_stride,
                                row_color+col_color))

        line_attr_array = temp_array.flatten().astype('u4')
        # line_attr_buffer = glCreateBuffers(1)
        self.line_attr_buffer = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.line_attr_buffer)
        # glBufferData(GL_SHADER_STORAGE_BUFFER, line_attr_array.nbytes, line_attr_array, GL_STATIC_DRAW)
        # glNamedBufferStorage(cliff_level_buffer, width * height * sizeof(float), nullptr, GL_DYNAMIC_STORAGE_BIT)
        glBufferStorage(GL_SHADER_STORAGE_BUFFER, line_attr_array.nbytes,
                        line_attr_array, GL_DYNAMIC_STORAGE_BIT)

        # for glDrawArraysInstanced execution
        # To run glDrawArraysInstanced without encountering an exception,
        # we should provide a 'vao' if we haven't done so already
        self.vao_dummy = glGenVertexArrays(1)
        glBindVertexArray(self.vao_dummy)

        self.line_attr_offset_location = 0

    def render(self,):
        glUseProgram(self.shader)

        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 2, self.line_attr_buffer)

        glBindVertexArray(self.vao_dummy)
        
        glUniform1ui(self.line_attr_offset_location, 0)
        glDrawArraysInstanced(GL_LINE_STRIP, 0, self.width_n, self.height_n)

        glUniform1ui(self.line_attr_offset_location, self.height_n)
        glDrawArraysInstanced(GL_LINE_STRIP, 0, self.height_n, self.width_n)

    def destroy(self) -> None:
        glDeleteProgram(self.shader)
        glDeleteBuffers(2, (self.line_attr_buffer, self.vao_dummy))


