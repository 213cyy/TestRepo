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


class Shader_Simple:
    # __slots__ = ("program", "single_uniforms", "multi_uniforms")

    def __init__(self, vertex_filepath: str, fragment_filepath: str):

        self.program = create_shader(vertex_filepath, fragment_filepath)

        self.single_uniforms: dict[int, int] = {}
        self.multi_uniforms: dict[int, list[int]] = {}

    def cache_single_location(self,
                              uniform_type: int, uniform_name: str) -> None:
        """
            Search and store the location of a uniform location.
            This is for uniforms which have one location per variable.
        """

        self.single_uniforms[uniform_type] = glGetUniformLocation(
            self.program, uniform_name)

    def cache_multi_location(self,
                             uniform_type: int, uniform_name: str) -> None:
        """
            Search and store the location of a uniform location.
            This is for uniforms which have multiple locations per variable.
            e.g. Arrays
        """

        if uniform_type not in self.multi_uniforms:
            self.multi_uniforms[uniform_type] = []

        self.multi_uniforms[uniform_type].append(
            glGetUniformLocation(
                self.program, uniform_name)
        )

    def fetch_single_location(self, uniform_type: int) -> int:
        """
            Returns the location of a uniform location.
            This is for uniforms which have one location per variable.
        """

        return self.single_uniforms[uniform_type]

    def fetch_multi_location(self,
                             uniform_type: int, index: int) -> int:
        """
            Returns the location of a uniform location.
            This is for uniforms which have multiple locations per variable.
            e.g. Arrays
        """

        return self.multi_uniforms[uniform_type][index]

    def use(self) -> None:
        glUseProgram(self.program)

    def destroy(self) -> None:
        glDeleteProgram(self.program)


class Shader:
    
    def __init__(self, vertex_filepath: str, fragment_filepath: str):
        self.program = create_shader(vertex_filepath, fragment_filepath)
        glUseProgram(self.program)

        self.projectMatrixLocation = glGetUniformLocation(self.program, "projection")
        self.modelMatrixLocation = glGetUniformLocation(self.program, "model")
        self.viewMatrixLocation = glGetUniformLocation(self.program, "view")
        self.colorLoc = glGetUniformLocation(self.program, "object_color")

    def use(self) -> None:
        glUseProgram(self.program)

    def destroy(self) -> None:
        glDeleteProgram(self.program)


class Shader_Tile:
    def __init__(self, vertex_filepath: str, fragment_filepath: str):
        self.program = create_shader(vertex_filepath, fragment_filepath)
        glUseProgram(self.program)

        self.projectMatrixLocation = glGetUniformLocation(self.program, "projection")
        self.modelMatrixLocation = glGetUniformLocation(self.program, "model")
        self.viewMatrixLocation = glGetUniformLocation(self.program, "view")
        self.tint = glGetUniformLocation(self.program, "tint")
    def use(self) -> None:
        glUseProgram(self.program)

    def destroy(self) -> None:
        glDeleteProgram(self.program)


# shader_table = {
#     "TILE": TileShader("shaders/vertex_tile.txt", "shaders/fragment_tile.txt"),
#     "STANDARD": Shader(
#         "shaders/vertex.txt", "shaders/fragment.txt"),
#     "EMISSIVE": Shader(
#         "shaders/vertex_light.txt",
#         "shaders/fragment_light.txt"),
#     "POST": Shader(
#         "shaders/simple_post_vertex.txt",
#         "shaders/post_processing_fragment.txt")
# }
