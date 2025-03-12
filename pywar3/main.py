import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
import numpy as np
import pyrr
from config import ENTITY_TYPE
from ground_default.tilemap import GroundRenderEngine
from game_s import Scene
from pipeline_shaders import *
from unit_mesh import *
from texture import *


SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

PIPELINE_TYPE = {
    "STANDARD": 0,
    "TILE": 1,
    "UNIT_DEFAULT": 2,
    "SIMPLE": 3,
}

UNIFORM_TYPE = {
    "AMBIENT": 0,
    "VIEW": 1,
    "PROJECTION": 2,
    "CAMERA_POS": 3,
    "LIGHT_COLOR": 4,
    "LIGHT_POS": 5,
    "OBJECT_COLOR": 6,
    "TINT": 7,
    "MODEL": 8,
}

GLOBAL_X = np.array([1, 0, 0], dtype=np.float32)
GLOBAL_Y = np.array([0, 1, 0], dtype=np.float32)
GLOBAL_Z = np.array([0, 0, 1], dtype=np.float32)


class App:
    """
        The control class.
    """
    # __slots__ = (
    #     "window", "renderer", "scene", "last_time",
    #     "current_time", "current_frames_rendered", "frametime",
    #     "_keys")

    def __init__(self):
        """
            Initialize the program.
        """

        self._set_up_glfw()

        self._set_up_timer()

        self._set_up_input_systems()

        self._create_assets()

    def _set_up_glfw(self) -> None:
        """
            Initialize and configure GLFW
        """

        glfw.init()
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_PROFILE,
            GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GLFW_CONSTANTS.GLFW_TRUE)
        # for uncapped framerate
        glfw.window_hint(GLFW_CONSTANTS.GLFW_DOUBLEBUFFER, GL_FALSE)
        self.window = glfw.create_window(
            SCREEN_WIDTH, SCREEN_HEIGHT, "Title", None, None)
        glfw.make_context_current(self.window)

    def _set_up_timer(self) -> None:
        """
            Initialize the variables used by the framerate
            timer.
        """
        self.last_time = glfw.get_time()
        self.current_time = 0
        self.last_frames_rendered = 0
        self.current_frames_rendered = 0
        self.frametime = 0.0

    def _set_up_input_systems(self) -> None:
        """
            Configure the mouse and keyboard
        """

        # glfw.set_input_mode(
        #     self.window,
        #     GLFW_CONSTANTS.GLFW_CURSOR,
        #     GLFW_CONSTANTS.GLFW_CURSOR_HIDDEN
        # )

        glfw.set_input_mode(
            self.window,
            GLFW_CONSTANTS.GLFW_CURSOR,
            GLFW_CONSTANTS.GLFW_CURSOR_NORMAL
        )

        self._keys = {}
        glfw.set_key_callback(self.window, self._key_callback)

    def _key_callback(self, window, key, scancode, action, mods) -> None:
        """
            Handle a key event.

            Parameters:

                window: the window on which the keypress occurred.

                key: the key which was pressed

                scancode: scancode of the key

                action: action of the key event

                mods: modifiers applied to the event
        """

        state = False
        if action == GLFW_CONSTANTS.GLFW_PRESS:
            state = True
        elif action == GLFW_CONSTANTS.GLFW_RELEASE:
            state = False
        else:
            return

        self._keys[key] = state

    def _create_assets(self) -> None:
        self.renderer = GraphicsEngine()
        self.scene = Scene()

    def run(self) -> None:
        """
            Run the program.
        """

        running = True
        while (running):
            # check events
            if glfw.window_should_close(self.window) \
                    or self._keys.get(GLFW_CONSTANTS.GLFW_KEY_ESCAPE, False):
                running = False

            self._handle_keys()
            # self._handle_mouse()

            glfw.poll_events()

            self.scene.update(self.frametime)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # self.renderer.render(
            #     self.scene.player, self.scene.entities
            self.renderer.render(self.scene.player,
                                 self.scene.ground,
                                 self.scene.entities,
                                 self.scene.units,
                                 self.scene.lights)

            # timing
            self._calculate_framerate()

    def _handle_keys(self) -> None:
        """
            Takes action based on the keys currently pressed.
        """

        d_pos_forward = 0
        d_pos_right = 0
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_W, False):
            d_pos_forward += 1
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_S, False):
            d_pos_forward -= 1
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_D, False):
            d_pos_right += 1
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_A, False):
            d_pos_right -= 1
        self.scene.move_player_camera_fb_rl(d_pos_forward, d_pos_right)

        d_pos_x = 0
        d_pos_y = 0
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_RIGHT, False):
            d_pos_x += 1
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_LEFT, False):
            d_pos_x -= 1
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_UP, False):
            d_pos_y += 1
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_DOWN, False):
            d_pos_y -= 1
        self.scene.move_player_camera_x_y(d_pos_x, d_pos_y)

        d_rotate_up = 0
        d_rotate_right = 0
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_PAGE_UP, False):
            d_rotate_up += 1
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_PAGE_DOWN, False):
            d_rotate_up -= 1
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_DELETE, False):
            d_rotate_right += 1
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_INSERT, False):
            d_rotate_right -= 1
        self.scene.move_player_camera_rotate(d_rotate_up, d_rotate_right)

        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_SCROLL_LOCK, False):
            self.scene.move_player_camera_lock_target()

        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_HOME, False):
            self.scene.move_player_camera_reset_camera()

        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_END, False):
            self.scene.move_player_camera_reset_target()

    def _handle_mouse(self) -> None:
        """
            spin the player based on the mouse movement
        """

        (x, y) = glfw.get_cursor_pos(self.window)
        d_eulers = 0.002 * ((SCREEN_WIDTH / 2) - x) * GLOBAL_Z
        d_eulers += 0.002 * ((SCREEN_HEIGHT / 2) - y) * GLOBAL_Y
        self.scene.spin_player(d_eulers)
        # glfw.set_cursor_pos(self.window, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    def _calculate_framerate(self) -> None:
        """
            Calculate the framerate and frametime,
            and update the window title.
        """

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

    def quit(self):

        self.renderer.destroy()
# endregion
####################### View  #################################################
# region


class GraphicsEngine:
    """
        Draws entities and stuff.
    """
    # __slots__ = ("meshes", "materials", "shaders", "framebuffer")

    def __init__(self):
        """
            Initializes the rendering system.
        """

        self._set_up_opengl()

        self._create_assets()

        self._set_onetime_uniforms()

        self._get_uniform_locations()

        self.ground_renderer = GroundRenderEngine()

    def _set_up_opengl(self) -> None:
        """
            Configure any desired OpenGL options
        """
        glClearColor(0.1, 0.2, 0.2, 1)
        # glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def _create_assets(self) -> None:
        """
            Create all of the assets needed for drawing.
        """
        preload_models = ["UNIT_TRIANGLE", "UNIT_CUBE", "UNIT_DEFAULT"]
        self.meshes: dict = {
            ENTITY_TYPE[m]: UNIT_ID_TO_MESH[ENTITY_TYPE[m]]() for m in preload_models
        }
        # self.meshes[ENTITY_TYPE["GROUND"]] = TileMap()
        # self.meshes: dict = {
        #     ENTITY_TYPE["TRIANGLE"]: Mesh_Triangle(),
        #     ENTITY_TYPE["UNIT_TRIANGLE"]: Mesh_Triangle()
        #     UNIT_ID_TO_MESH={ENTITY_TYPE["UNIT_TRIANGLE"]:Mesh_Triangle,
        #         ENTITY_TYPE["UNIT_CUBE"]:Mesh_Cube}
        # ENTITY_TYPE["GROUND"]: Grid(48),
        # ENTITY_TYPE["CUBE"]: TexturedQuad(0, 0, 2, 2),
        #
        # ENTITY_TYPE["MEDKIT"]: BillBoardMesh(w = 0.6, h = 0.5),
        # }

        # color_buffer = ColorAttachment()
        # depth_buffer = DepthStencilAttachment()
        # self.framebuffer = FrameBuffer((color_buffer,), depth_buffer)

        materials = {}
        for m in preload_models:
            unit_id = ENTITY_TYPE[m]
            if unit_id in UNIT_ID_TO_MATERIAL:
                materials[unit_id] = UNIT_ID_TO_MATERIAL[unit_id]()
        self.materials: dict[int, Texture_Raw] = materials
        # self.materials: dict[int, Material] = {
        #     ENTITY_TYPE["CUBE"]: AdvancedMaterial("wood", "png"),
        #     ENTITY_TYPE["MEDKIT"]: AdvancedMaterial("medkit", "png"),
        #     ENTITY_TYPE["POINTLIGHT"]: Material2D("gfx/greenlight.png", 0),
        #     ENTITY_TYPE["SCREEN"]: color_buffer,
        # }

        self.shaders: dict = {
            PIPELINE_TYPE["STANDARD"]: Shader("shaders/vertex.txt", "shaders/fragment.txt"),
            PIPELINE_TYPE["UNIT_DEFAULT"]: Shader("shaders/unit_vertex.txt", "shaders/unit_fragment.txt"),
            # PIPELINE_TYPE["TILE"]: Shader_Tile("shaders/ground_vertex.txt", "shaders/ground_fragment.txt"),
            PIPELINE_TYPE["SIMPLE"]: Shader_Simple("shaders/vertex_simple.txt", "shaders/fragment_simple.txt"),

        }

    def _set_onetime_uniforms(self) -> None:
        """
            Some shader data only needs to be set once.
        """

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy=45, aspect=SCREEN_WIDTH/SCREEN_HEIGHT,
            near=0.1, far=5000, dtype=np.float32
        )

        shader_type = PIPELINE_TYPE["STANDARD"]
        shader = self.shaders[shader_type]
        shader.use()

        glUniformMatrix4fv(
            glGetUniformLocation(shader.program, "projection"),
            1, GL_FALSE, projection_transform
        )

        # shader_type = PIPELINE_TYPE["TILE"]
        # shader = self.shaders[shader_type]
        # shader.use()



    def _get_uniform_locations(self) -> None:
        """
            Query and store the locations of shader uniforms
        """

        shader_type = PIPELINE_TYPE["SIMPLE"]
        shader = self.shaders[shader_type]
        shader.use()

        shader.cache_single_location(UNIFORM_TYPE["MODEL"], "model")
        shader.cache_single_location(UNIFORM_TYPE["VIEW"], "view")
        shader.cache_single_location(UNIFORM_TYPE["PROJECTION"], "projection")
        shader.cache_single_location(
            UNIFORM_TYPE["OBJECT_COLOR"], "object_color")

        # shader.cache_single_location(
        #     UNIFORM_TYPE["CAMERA_POS"], "viewPos")

        # shader_type = PIPELINE_TYPE["TILE"]
        # shader = self.shaders[shader_type]
        # shader.use()

        # shader.cache_single_location(UNIFORM_TYPE["MODEL"], "model")
        # shader.cache_single_location(UNIFORM_TYPE["VIEW"], "view")
        # shader.cache_single_location(UNIFORM_TYPE["TINT"], "tint")

    def render(self,
               camera,
               ground,
               renderables,
               units,
               lights: list) -> None:

        # glUseProgram(selfshader)
        # selftriangle.arm_for_drawing()
        # selftriangle.draw()

        # modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        # glUniformMatrix4fv(shader.modelMatrixLocation,
        #                    1, GL_FALSE, modelTransform)

        shader_type = PIPELINE_TYPE["STANDARD"]
        shader = self.shaders[shader_type]
        shader.use()

        projection = camera.get_projection_transform(
            SCREEN_WIDTH/SCREEN_HEIGHT)
        glUniformMatrix4fv(shader.projectMatrixLocation,
                           1, GL_FALSE, projection)

        view = camera.get_view_transform()
        glUniformMatrix4fv(shader.viewMatrixLocation,
                           1, GL_FALSE, view)

        for entity_type_id, entities in renderables.items():

            if entity_type_id not in self.meshes:
                continue
            mesh = self.meshes[entity_type_id]
            mesh.arm_for_drawing()
            # self.materials[entity_type_id].use()

            for entity in entities:
                glUniform3fv(shader.colorLoc,
                             1, entity.color)
                glUniformMatrix4fv(shader.modelMatrixLocation,
                                   1, GL_FALSE, entity.get_model_transform())
                mesh.draw()

        shader_type = PIPELINE_TYPE["UNIT_DEFAULT"]
        shader = self.shaders[shader_type]
        shader.use()

        projection = camera.get_projection_transform(
            SCREEN_WIDTH/SCREEN_HEIGHT)
        glUniformMatrix4fv(shader.projectMatrixLocation,
                           1, GL_FALSE, projection)

        view = camera.get_view_transform()
        glUniformMatrix4fv(shader.viewMatrixLocation,
                           1, GL_FALSE, view)

        for entity_type_id, entities in units.items():

            mesh = self.meshes[entity_type_id]
            mesh.arm_for_drawing()
            self.materials[entity_type_id].use()

            for entity in entities:
                glUniform3fv(shader.colorLoc,
                             1, entity.color)
                glUniformMatrix4fv(shader.modelMatrixLocation,
                                   1, GL_FALSE, entity.get_model_transform())
                mesh.draw()



        projection = camera.get_projection_transform(
            SCREEN_WIDTH/SCREEN_HEIGHT)
        view = camera.get_view_transform()
        self.ground_renderer.render(view,projection)
        # self.ground_renderer.render()









        # First pass
        # self.framebuffer.use()
        # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # glEnable(GL_DEPTH_TEST)

        # lit shader
        # shader_type = PIPELINE_TYPE["STANDARD"]
        # shader = self.shaders[shader_type]
        # shader.use()

        # # glUniform3fv(
        # #     shader.fetch_single_location(UNIFORM_TYPE["CAMERA_POS"]),
        # #     1, camera.position)

        # modelTransform = pyrr.matrix44.multiply(
        #     m1 = modelTransform,
        #     m2 = pyrr.matrix44.create_from_translation(vec = np.array([-16, -24, 0], dtype=np.float32))
        # )

        # glUniformMatrix4fv(
        #     shader.fetch_single_location(UNIFORM_TYPE["MODEL"]),
        #     1, GL_FALSE, entity.get_model_transform())
        # shader_type = PIPELINE_TYPE["TILE"]
        # shader = self.shaders[shader_type]
        # shader.use()

        # glUniformMatrix4fv(
        #     shader.fetch_single_location(UNIFORM_TYPE["VIEW"]),
        #     1, GL_FALSE, view)

        # glUniform3fv(
        #     shader.fetch_single_location(UNIFORM_TYPE["CAMERA_POS"]),
        #     1, camera.position)

        print(glGetError())
        glFlush()

    def destroy(self) -> None:
        """ free any allocated memory """

        # self.framebuffer.destroy()
        for mesh in self.meshes.values():
            mesh.destroy()
        for material in self.materials.values():
            material.destroy()
        for shader in self.shaders.values():
            shader.destroy()


my_app = App()
my_app.run()
my_app.quit()
