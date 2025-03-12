from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np



import importlib.util
import sys




file_path = 'E:\Documents\pyCode\paperwar3\pywar3\ground\TerrainArt\Cliffs\cliff_data.py'
module_name = 'your_module'

# Load the module
spec = importlib.util.spec_from_file_location(module_name, file_path)
module = importlib.util.module_from_spec(spec)
# sys.modules[module_name] = module
spec.loader.exec_module(module)

# Example usage
# Use the functions or classes from the imported module
your_module.some_function()


# [k.pos_x,k.pos_y,k.pos_ground_z,k.pos_water_z ] for k in corner_list ]
# x = [k * 128 + self.center_offset_x for k in range(self.width)]
# y = [k * 128 + self.center_offset_y for k in range(self.height)]
# z = [k.pos_ground_z for k in corner_list]

# xyz = np.dstack((xx.ravel(), yy.ravel(), z)).ravel()
# indices = indices.reshape(self._height, -1).flatten('f')
     
pass
class MapShader:

    def create_shader(self , vertex_filepath: str, fragment_filepath: str):

        with open(vertex_filepath, 'r') as f:
            vertex_src = f.readlines()
        with open(fragment_filepath, 'r') as f:
            fragment_src = f.readlines()
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))

        return shader

    def __init__(self, ):
        
        glUseProgram(self.program)

        # self.projectMatrixLocation = glGetUniformLocation(
        #     self.program, "projection")
        # self.modelMatrixLocation = glGetUniformLocation(self.program, "model")
        # self.viewMatrixLocation = glGetUniformLocation(self.program, "view")
        # self.tint = glGetUniformLocation(self.program, "tint")

###########################################################

