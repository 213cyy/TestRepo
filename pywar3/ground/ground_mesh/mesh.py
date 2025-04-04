
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GL import GL_VERTEX_SHADER,GL_FRAGMENT_SHADER

class Mesh:
    def __init__(self):
        pass 

    def create_shader(self, vertex_filepath: str, fragment_filepath: str):

        with open(vertex_filepath, 'r') as f:
            vertex_src = f.readlines()
        with open(fragment_filepath, 'r') as f:
            fragment_src = f.readlines()
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))

        return shader
