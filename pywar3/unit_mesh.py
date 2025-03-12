from OpenGL.GL import *
from config import *
import numpy as np


class Mesh_Triangle:
    """
        Yep, it's a triangle.
    """

    def __init__(self):
        """
            Initialize a triangle.
        """

        # x, y, z, r, g, b
        vertices = (
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
            0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
            0.0,  0.5, 0.0, 0.0, 0.0, 1.0
        )
        vertices = 10*np.array(vertices, dtype=np.float32)
        import struct
        vertices = struct.pack('18f', *vertices)
        self.vertex_count = 3

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        # sizeofv = vertices.nbytes
        sizeofv = len(vertices)
        glBufferData(GL_ARRAY_BUFFER, sizeofv, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE,
                              24, ctypes.c_void_p(12))

        glBindVertexArray(0)

    def arm_for_drawing(self) -> None:
        """
            Arm the triangle for drawing.
        """
        glBindVertexArray(self.vao)

    def draw(self) -> None:
        """
            Draw the triangle.
        """
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self) -> None:
        """
            Free any allocated memory.
        """
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))







UNIT_ID_TO_MESH = {ENTITY_TYPE["UNIT_TRIANGLE"]: Mesh_Triangle,
                   ENTITY_TYPE["UNIT_CUBE"]: Mesh_Cube,
                   ENTITY_TYPE["UNIT_DEFAULT"]: Mesh_Default,
                   }
