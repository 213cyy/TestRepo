from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr

def create_shader(vertex_filepath: str, fragment_filepath: str) -> int:

    with open(vertex_filepath, 'r') as f:
        vertex_src = f.readlines()

    with open(fragment_filepath, 'r') as f:
        fragment_src = f.readlines()

    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))

    return shader


class Shader:
    
    def __init__(self, vertex_filepath: str, fragment_filepath: str):
        self.program = create_shader(vertex_filepath, fragment_filepath)
        glUseProgram(self.program)

        self.projectMatrixLocation = glGetUniformLocation(self.program, "projection")
        self.modelMatrixLocation = glGetUniformLocation(self.program, "model")
        self.viewMatrixLocation = glGetUniformLocation(self.program, "view")
        self.colorLoc = glGetUniformLocation(self.program, "object_color")
        self.tintLoc = glGetUniformLocation(self.program, "tint")

    def use(self) -> None:
        glUseProgram(self.program)

    def destroy(self) -> None:
        glDeleteProgram(self.program)








