from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from struct import unpack, iter_unpack, Struct
import numpy as np
from PIL import Image

if __name__ == "__main__":
    from conf import *
else:
    from ground_default.conf import *








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
