from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import numpy as np
import time
from PIL import Image

if __name__ == "__main__":
    from conf import *
else:
    from mark_line.conf import *


class Mark_Agent:
    def __init__(self, auto_update=False, screen_width=640, screen_height=480):
        self.auto_update_flag = auto_update

        if auto_update:
            self.last_update_time = time.time()
            self.cursor_stat = 0

        self.color = [0.5, 0.9, 1.0]
        self.drag_select_flag = False
        self.start_point = np.random.uniform(-1, 1, size=2)
        self.end_point = self.start_point.copy()
        # SCREEN_WIDTH = 640
        # SCREEN_HEIGHT = 480
        self.update_with_screen_size(screen_width, screen_height)

    def update(self, mouse_stat, dt_frametime):
        pass

    def update_with_screen_size(self, width, height):
        k = width/height
        a, b = 0.08, 0.02
        vertices = (
            -a, 0.0, -b, 0.0,  b, 0.0, a, 0.0,
            0.0, -a*k, 0.0, -b*k, 0.0,  b*k, 0.0, a*k,
        )
        self.vertex_crosshairs = np.array(vertices, dtype=np.float32)
        l = 0.1
        offset = 0.02
        vertices = (
            0-offset, -l*k+offset, 0, 0,
            l-offset, -l*k+offset, 1, 0,
            0-offset, 0+offset, 0, 1,
            l-offset, -l*k+offset, 1, 0,
            l-offset, 0+offset, 1, 1,
            0-offset, 0+offset, 0, 1,
        )
        self.vertex_cursor = np.array(vertices, dtype=np.float32)

    def auto_update(self,):
        if not self.auto_update_flag:
            return

        current_time = time.time()
        dt_frame = current_time - self.last_update_time
        if dt_frame > 0.150:
            self.cursor_stat = (self.cursor_stat+1) % 8
            # print(self.cursor_stat)
            self.last_update_time = current_time

        dxy = self.start_point / sum(self.start_point)
        self.end_point -= dxy * dt_frame * 0.005

        x, y = self.end_point
        if not (-1 < x < 1 and -1 < y < 1):
            self.drag_select_flag = not self.drag_select_flag
            self.start_point = np.random.uniform(-1, 1, size=2)
            self.end_point = self.start_point.copy()


class MarkLineRenderEngine:
    # Auxiliary lines
    def create_shader(self, vertex_filepath: str, fragment_filepath: str):

        with open(vertex_filepath, 'r') as f:
            vertex_src = f.readlines()
        with open(fragment_filepath, 'r') as f:
            fragment_src = f.readlines()
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))

        return shader

    def __init__(self, auto_update=False):

        self.agent = Mark_Agent(auto_update,)
        self.texture = CursorTexture()

        self.program = self.create_shader(
            MARK_SHADER_FOLDER + "markline.vert",
            MARK_SHADER_FOLDER + "markline.frag")

        self.crosshairs_vao = glGenVertexArrays(1)
        glBindVertexArray(self.crosshairs_vao)

        vertices = self.agent.vertex_crosshairs
        self.crosshairs_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.crosshairs_vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes,
                     vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

        # #######################
        self.cursor_vao = glGenVertexArrays(1)
        glBindVertexArray(self.cursor_vao)

        vertices = self.agent.vertex_cursor
        self.cursor_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.cursor_vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes,
                     vertices, GL_STATIC_DRAW)
        # position_z
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))
        glBindVertexArray(0)

        glUseProgram(self.program)
        self.branchID_1ui = glGetUniformLocation(self.program, "branch_ID")

        self.colorLoc_3f = glGetUniformLocation(self.program, "inColor")
        self.rectPoint_4f = glGetUniformLocation(self.program, "inRect")
        self.layerIndex_1ui = glGetUniformLocation(
            self.program, "texture_layer")

    def update_with_screen_size(self, width, height):
        self.agent.update_with_screen_size(width, height)
        vertices = self.agent.vertex_crosshairs
        glBindBuffer(GL_ARRAY_BUFFER, self.crosshairs_vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes,
                     vertices, GL_STATIC_DRAW)
        vertices = self.agent.vertex_cursor
        glBindBuffer(GL_ARRAY_BUFFER, self.cursor_vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes,
                     vertices, GL_STATIC_DRAW)

    def render(self, mark_dummy=None):
        glUseProgram(self.program)

        glUniform3f(self.colorLoc_3f, *self.agent.color)
        glUniform4f(self.rectPoint_4f, *self.agent.start_point,
                    *self.agent.end_point)

        glUniform1ui(self.branchID_1ui,  0)
        glBindVertexArray(self.crosshairs_vao)
        glDrawArrays(GL_LINES, 0, 8)

        if self.agent.drag_select_flag:

            glUniform1ui(self.branchID_1ui,  2)
            glDrawArrays(GL_LINE_LOOP, 0, 4)

        glUniform1ui(self.branchID_1ui,  1)
        glBindVertexArray(self.cursor_vao)
        self.texture.use()
        glUniform1ui(self.layerIndex_1ui,  self.agent.cursor_stat)
        glDrawArrays(GL_TRIANGLES, 0, 6)

        self.agent.auto_update()

    def destroy(self) -> None:
        glDeleteProgram(self.program)
        glDeleteVertexArrays(2, (self.crosshairs_vao, self.cursor_vao))
        glDeleteBuffers(2, (self.crosshairs_vbo, self.cursor_vbo))


class CursorTexture():
    # Water textures
    tile_size = 32
    tile_num = 32
    lods = 8  # log2(128) + 1
    image_width = 256
    image_height = 128

    def __init__(self,):
        # glCreateTextures(GL_TEXTURE_2D_ARRAY, 1, &water_texture_array)
        # glTextureStorage3D(water_texture_array, self.lods, GL_RGBA8, 128, 128, WATER_TEXTURES_NUM)
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.texture)
        glTexStorage3D(GL_TEXTURE_2D_ARRAY, 1, GL_RGBA8,
                       32, 32, 32)
        glTexParameteri(GL_TEXTURE_2D_ARRAY,
                        GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D_ARRAY,
                        GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D_ARRAY,
                        GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        filepath = CURSOR_TEXTURE_FILE
        FLIP_TOP_BOTTOM = 1
        with Image.open(filepath, mode="r") as image:
            # image_width,image_height = img.size # for texture size check
            for ind in range(32):
                y, x = divmod(ind, 8)
                xx, yy = 32*x, 32*y
                img = image.crop((xx, yy, xx+32, yy+32)
                                 ).transpose(method=FLIP_TOP_BOTTOM)

                # glTexSubImage3D(target,level,xoffset,yoffset,zoffset,width,height,depth,format,type,pixels)
                glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0,
                                0, 0, ind, 32, 32, 1,
                                GL_RGBA, GL_UNSIGNED_BYTE, img.tobytes())

        # glGenerateMipmap(GL_TEXTURE_2D_ARRAY)

    def use(self) -> None:
        # glBindTextureUnit(GL_TEXTURE0 + unit, texture)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.texture)

    def destroy(self) -> None:
        glDeleteTextures(1, (self.texture,))


if __name__ == "__main__":
    print(10 * "-", "for debug")
    SCREEN_WIDTH = 640
    SCREEN_HEIGHT = 480
    import glfw
    import glfw.GLFW as GLFW_CONSTANTS

    glfw.init()
    # glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR, 3)
    # glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR, 3)
    # glfw.window_hint(
    #     GLFW_CONSTANTS.GLFW_OPENGL_PROFILE,
    #     GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
    # glfw.window_hint(
    #     GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GLFW_CONSTANTS.GLFW_TRUE)
    # # for uncapped framerate
    glfw.window_hint(GLFW_CONSTANTS.GLFW_DOUBLEBUFFER, GL_FALSE)
    window = glfw.create_window(
        SCREEN_WIDTH, SCREEN_HEIGHT, "for debug", None, None)
    glfw.make_context_current(window)
    # glEnable(GL_TEXTURE_3D)
    glClearColor(0.1, 0.2, 0.2, 1)
    # glClear(GL_COLOR_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # glEnable(GL_TEXTURE_2D_ARRAY)

    marker = MarkLineRenderEngine(auto_update=True)

    running = True
    while (running):
        # check events
        if glfw.window_should_close(window):
            running = False

        # self._handle_keys()
        # self._handle_mouse()
        # self.scene.update(self.frametime)

        glfw.poll_events()

        # glClearColor(0.5, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        marker.render()
        # glfwSwapBuffers(window)
        glFlush()

        # timing_calculate_framerate()
