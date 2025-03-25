import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *

import numpy as np
import pyrr

from config import *

from ground.ground_default import GroundRenderEngine
from camera.camera_default import Camera
from game_scene import GameManager


class App:

    def __init__(self):
        self.window_state = {
            'windows_size': (DEFAULT_SCREEN_WIDTH,  DEFAULT_SCREEN_HEIGHT),
            'mouse_position': (0, 0),
            'frametime': 0,
        }

        self._set_up_glfw()

        # _after_set_up_glfw
        self.ground = GroundRenderEngine()
        self.camera = Camera()
        self.game_manager = GameManager(self)
        self.engine_manager_list = []
        self.keys_state = {}

        self._set_up_timer()

        self._set_up_input_systems()

    def _set_up_glfw(self) -> None:
        glfw.init()
        # glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR, 3)
        # glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR, 3)
        # glfw.window_hint(
        #     GLFW_CONSTANTS.GLFW_OPENGL_PROFILE,
        #     GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
        # glfw.window_hint(
        #     GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GLFW_CONSTANTS.GLFW_TRUE)
        # for uncapped framerate
        # glfw.window_hint(GLFW_CONSTANTS.GLFW_DOUBLEBUFFER, GL_FALSE)
        self.window = glfw.create_window(
            DEFAULT_SCREEN_WIDTH,  DEFAULT_SCREEN_HEIGHT, "Title", None, None)
        glfw.make_context_current(self.window)

    def _set_up_timer(self) -> None:
        self.last_time = glfw.get_time()
        self.current_time = 0
        self.last_frames_rendered = 0
        self.current_frames_rendered = 0
        self.frametime = 0.0

    def _set_up_input_systems(self) -> None:
        # GLFW_CONSTANTS.GLFW_CURSOR_HIDDEN
        glfw.set_input_mode(
            self.window,
            GLFW_CONSTANTS.GLFW_CURSOR,
            GLFW_CONSTANTS.GLFW_CURSOR_NORMAL
        )

        glfw.set_key_callback(self.window, self._key_callback)
        glfw.set_framebuffer_size_callback(
            self.window, self._buffer_size_callback)

    def _key_callback(self, window, key, scancode, action, mods) -> None:
        if action == GLFW_CONSTANTS.GLFW_PRESS:
            # self.keys_state[key] = self.keys_state.get(key, 0)+ 1
            self.keys_state[key] = True
        elif action == GLFW_CONSTANTS.GLFW_RELEASE:
            # self.keys_state[key] = 0
            self.keys_state[key] = False

    def _buffer_size_callback(self, window, width, height) -> None:
        glViewport(0, 0, width, height)
        self.window_state['windows_size'] = (width, height)

    def add_manager(self, manager) -> None:
        self.engine_manager_list .append(manager)

    def _set_up_opengl(self) -> None:
        # glEnable(GL_TEXTURE_3D)
        # glEnable(GL_TEXTURE_2D_ARRAY)
        # glClearColor(0.5, 0.1, 0.1, 1.0)
        glClearColor(0.1, 0.2, 0.2, 1)
        # glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # glBlendFunc(GL_SRC_ALPHA, GL_SRC_ALPHA)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_DST_ALPHA)

    def run(self) -> None:
        self._set_up_opengl()
        running = True
        while (running):
            # check events
            if glfw.window_should_close(self.window) \
                    or self.keys_state.get(GLFW_CONSTANTS.GLFW_KEY_ESCAPE, False):
                running = False

            glfw.poll_events()

            # self._handle_keys()
            # self._handle_mouse()
            self.camera.update_with_input(self.keys_state, self.window_state)
            self.update_window_state()

            self.ground.update_with_input(self.keys_state, self.window_state)
            self.game_manager.update_with_input(
                self.keys_state, self.window_state)
            for engine in self.engine_manager_list:
                engine.update_with_input(self.keys_state, self.window_state)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            self.ground.render()
            self.game_manager.render()
            for engine in self.engine_manager_list:
                engine.render()

            glFlush()
            glfw.swap_buffers(self.window)

    def update_window_state(self):
        (x, y) = mouse_pos = glfw.get_cursor_pos(self.window)
        self.window_state['mouse_position'] = mouse_pos
        # timing
        self.window_state['frametime'] = self.calculate_framerate()
        self.window_state['mvp'] = self.camera.get_view_projection()

        if not self.camera.target_lock_flag:
            width, height = self.window_state['windows_size']
            glfw.set_cursor_pos(self.window, width / 2, height / 2)

    def calculate_framerate(self) -> None:
        self.current_frames_rendered += 1
        self.current_time = glfw.get_time()
        delta = self.current_time - self.last_time
        if (delta >= 1):
            frameincrease = self.current_frames_rendered-self.last_frames_rendered
            framerate = max(1, int(frameincrease/delta))
            glfw.set_window_title(self.window, f"Running at {framerate} fps.")

            self.last_frames_rendered = self.current_frames_rendered
            self.last_time = self.current_time

            self.frametime = float(1000.0 / max(1, framerate))
            # print(self.frametime)
        return self.frametime

    def quit(self):
        self.game_manager.destroy()
        for engine in self.engine_manager_list:
            engine.destroy()
        glfw.terminate()

# 
######################################################################
# 


if __name__ == '__main__':

    my_app = App()
    my_app.run()
    my_app.quit()
