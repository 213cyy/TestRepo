import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
import numpy as np
import pyrr


class aaaaaaaaa:

    def __init__(self):
        self.program = 1
        self.projectMatrixLocation = glGetUniformLocation(
            self.program, "projection")
        self.modelMatrixLocation = glGetUniformLocation(self.program, "model")
        self.viewMatrixLocation = glGetUniformLocation(self.program, "view")
        self.colorLoc = glGetUniformLocation(self.program, "object_color")

    def _create_assets(self) -> None:
        color_buffer = ColorAttachment()
        depth_buffer = DepthStencilAttachment()
        self.framebuffer = FrameBuffer((color_buffer,), depth_buffer)

    def render(self, camera):
        modelTransform = projection = view = \
            pyrr.matrix44.create_identity(dtype=np.float32)
        glUniformMatrix4fv(self.modelMatrixLocation,
                           1, GL_FALSE, modelTransform)
        glUniformMatrix4fv(self.projectMatrixLocation,
                           1, GL_FALSE, projection)
        glUniformMatrix4fv(self.viewMatrixLocation,
                           1, GL_FALSE, view)

        color = [1, 1, 1]
        glUniform3fv(self.colorLoc, 1, color)



