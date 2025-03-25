import glfw.GLFW as GLFW_CONSTANTS

import numpy as np
import pyrr


class Camera():
    # initialPosition = (0,0,0) 
    # __slots__ = ("forwards", "right", "up")
    # CAMERA_FIELD_FARZ
    # CAMERA_FIELD_ROTATION
    # CAMERA_FIELD_ZOFFSET

    # CAMERA_FIELD_FIELD_OF_VIEW
    CAMERA_DEFAULT_FIELD_OF_VIEW = 70.0/2
    # CAMERA_FIELD_TARGET_DISTANCE
    TARGET_DEFAULT_DISTANCE = d = 1650.00
    # CAMERA_FIELD_ANGLE_OF_ATTACK
    CAMERA_DEFAULT_ANGLE_OF_ATTACK = pitch = np.deg2rad(304.00)
    CAMERA_DEFAULT_VECTOR_FROM_TARGET = np.array(
        [0, -d*np.cos(pitch), -d*np.sin(pitch)], dtype=np.float32)
    # CAMERA_FIELD_ROLL
    CAMERA_ROLL = 0

    def __init__(self):
        self.animate_period = 5000
        self.animate_distance_pms = 2000/5000
        self.animate_radian_pms = 3.1415/5000

        self.window_aspect = 4/3
        # position = [0,0,-20]
        self.target = np.array([0, 0, 0], dtype=np.float32)
        self.position = self.target + self.CAMERA_DEFAULT_VECTOR_FROM_TARGET
        self.local_eulers = None

        self.target_lock_flag = True
        self.interval_time = 50
        self.update()

    def update(self) -> None:
        self.forwards = pyrr.vector.normalize(self.target - self.position)
        # print(list(self.forwards))
        # theta = self.eulers[2]
        # phi = self.eulers[1]

        # self.forwards = np.array(
        #     [
        #         np.cos(np.deg2rad(theta)) * np.cos(np.deg2rad(phi)),
        #         np.sin(np.deg2rad(theta)) * np.cos(np.deg2rad(phi)),
        #         np.sin(np.deg2rad(phi))
        #     ],
        #     dtype=np.float32
        # )
        self.right = np.cross(self.forwards, np.array(
            [0, 0, 1], dtype=np.float32))

        self.up = np.cross(self.right, self.forwards)

    def get_projection_transform(self):
        return pyrr.matrix44.create_perspective_projection(
            fovy=self.CAMERA_DEFAULT_FIELD_OF_VIEW, 
            aspect=self.window_aspect,
            near=16, far=5000, dtype=np.float32
        )
        # return projection_transform

    def get_view_transform(self) -> np.ndarray:
        return pyrr.matrix44.create_look_at(
            eye=self.position,
            target=self.target,
            up=self.up, dtype=np.float32)

    def get_view_projection(self):
        # Model-View-Projection
        # MVP = projection.T@view.T
        view = self.get_view_transform()
        projection = self.get_projection_transform()
        MVP = view @ projection
        # MVP = projection @ view 
        return MVP

    ####################################################

    def move_x_y(self, x, y):
        inter_vector = self.animate_distance_pms * \
            np.array([x, y, 0], dtype=np.float32)
        self.target += self.interval_time*inter_vector
        self.position += self.interval_time*inter_vector

    def move_fb_rl(self, f, r):
        interval = self.animate_distance_pms * self.interval_time
        self.target += interval * r * self.right
        self.position += interval *  r * self.right
        new_pos = self.position + interval * f * self.forwards
        if np.linalg.norm(self.target - new_pos) > 150:
            self.position =new_pos

    def move_rotate(self, u, r):
        interval = self.animate_radian_pms * self.interval_time

        m_ry =pyrr.matrix33.create_from_axis_rotation(
            axis=self.right,
            theta=interval * u,
            dtype=np.float32
        )

        m_rz=pyrr.matrix33.create_from_axis_rotation(
            axis=[0,0,1],
            theta=interval * r,
            dtype=np.float32
        )

        inter_vector= self.position - self.target
        self.position = self.target + (inter_vector  @ m_ry @ m_rz)


    def target_rotate(self,dx,dy):
        interval = self.animate_radian_pms * self.interval_time

        up = -dy * 200
        # print(up)
        m_ry =pyrr.matrix33.create_from_axis_rotation(
            axis=self.right,
            theta=interval * up,
            dtype=np.float32
        )

        right = -dx * 200
        # print(right)
        m_rz=pyrr.matrix33.create_from_axis_rotation(
            axis=self.up,
            theta=interval * right,
            dtype=np.float32
        )

        inter_vector= self.target - self.position 
        self.target = self.position + (inter_vector  @ m_ry @ m_rz)

    def reset_camera(self,):
        self.target_lock_flag = True
        self.target[2] = 0
        self.position = self.target + self.CAMERA_DEFAULT_VECTOR_FROM_TARGET

    def reset_target(self,):
        self.target_lock_flag = True
        self.target = np.array([0, 0, 0], dtype=np.float32)
        self.position = self.target + self.CAMERA_DEFAULT_VECTOR_FROM_TARGET


    def toggle_target_lock(self):
        print(self.target_lock_flag)
        if self.target_lock_flag :
            self.target_lock_flag = False
        else :
            self.target_lock_flag = True
            self.target[2] = 0

    def update_with_input(self,keys_state, window_state):
        width, height = window_state['windows_size']
        # SCREEN_WIDTH/SCREEN_HEIGHT
        if height == 0 :
            width,height = 1,1
        self.window_aspect =  width/height

        self.interval_time = window_state['frametime'] 

        """
            Takes action based on the keys currently pressed.
        """

        if not self.target_lock_flag :
            mouse_x,mouse_y = window_state['mouse_position']
            dx,dy=mouse_x/width - 1 /2 , mouse_y /height - 1/2
            self.target_rotate(dx,dy)

        if not "meetsomecondition":
            width, height = self.window_state['windows_size']
            glfw.set_cursor_pos(self.window, width / 2, height / 2)

        d_pos_forward = 0
        d_pos_right = 0
        if keys_state.get(GLFW_CONSTANTS.GLFW_KEY_W, False):
            d_pos_forward += 1
        if keys_state.get(GLFW_CONSTANTS.GLFW_KEY_S, False):
            d_pos_forward -= 1
        if keys_state.get(GLFW_CONSTANTS.GLFW_KEY_D, False):
            d_pos_right += 1
        if keys_state.get(GLFW_CONSTANTS.GLFW_KEY_A, False):
            d_pos_right -= 1
        if d_pos_forward!=0  or d_pos_right!=0 : 
            self.move_fb_rl(d_pos_forward,d_pos_right)

        d_pos_x = 0
        d_pos_y = 0
        if keys_state.get(GLFW_CONSTANTS.GLFW_KEY_RIGHT, False):
            d_pos_x += 1
        if keys_state.get(GLFW_CONSTANTS.GLFW_KEY_LEFT, False):
            d_pos_x -= 1
        if keys_state.get(GLFW_CONSTANTS.GLFW_KEY_UP, False):
            d_pos_y += 1
        if keys_state.get(GLFW_CONSTANTS.GLFW_KEY_DOWN, False):
            d_pos_y -= 1
        if d_pos_x!=0  or d_pos_y!=0 : 
            self.move_x_y(d_pos_x,d_pos_y)

        d_rotate_up = 0
        d_rotate_right = 0
        if keys_state.get(GLFW_CONSTANTS.GLFW_KEY_PAGE_UP, False):
            d_rotate_up += 1
        if keys_state.get(GLFW_CONSTANTS.GLFW_KEY_PAGE_DOWN, False):
            d_rotate_up -= 1
        if keys_state.get(GLFW_CONSTANTS.GLFW_KEY_DELETE, False):
            d_rotate_right += 1
        if keys_state.get(GLFW_CONSTANTS.GLFW_KEY_INSERT, False):
            d_rotate_right -= 1
        if d_rotate_up!=0  or d_rotate_right!=0 : 
            self.move_rotate(d_rotate_up,d_rotate_right)

        if keys_state.get(GLFW_CONSTANTS.GLFW_KEY_SCROLL_LOCK, False):
            self.toggle_target_lock()
            keys_state[GLFW_CONSTANTS.GLFW_KEY_SCROLL_LOCK] = False

        if keys_state.get(GLFW_CONSTANTS.GLFW_KEY_HOME, False):
            self.reset_camera()
            keys_state[GLFW_CONSTANTS.GLFW_KEY_HOME] = False

        if keys_state.get(GLFW_CONSTANTS.GLFW_KEY_END, False):
            # print('sdf')
            self.reset_target()
            keys_state[GLFW_CONSTANTS.GLFW_KEY_END] = False

        self.update()


if __name__ == "__main__":
    print(10 * "-", "debug", 10 * "-")

    from conf import *
    from sys import path
    path.append(ROOT)

    from main import App
    my_app = App()
    # my_app.set_ground(GroundRenderEngine())
    # my_app.add_manager(GroundRenderEngine())
    my_app.run()
    my_app.quit()