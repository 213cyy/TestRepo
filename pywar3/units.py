from OpenGL.GL import *
from config import *
import numpy as np
import pyrr



class Unit_Triangle(Entity):
    unit_type_name = "UNIT_TRIANGLE"

    def __init__(self, player_id=0, x=0, y=0, face=270):
        self.player_id = player_id
        self.animate_time = 0
        self.animate_period = 5000
        color = PLAYER_COLORS[player_id]
        super().__init__([x, y, 0], [0,face, 0], color)

    def update(self, frametime, camera_pos: np.ndarray) -> None:
        self.position[2] = 10*np.sin(self.animate_time)
        self.animate_time += 2*3.1415926 * frametime / self.animate_period





class BillBoard(Entity):

    __slots__ = tuple()

    def __init__(self, position: list):


        super().__init__(position, eulers=[0, 0, 0])

    def update(self, dt: float, camera_pos: np.ndarray) -> None:


        self_to_camera = camera_pos - self.position
        self.eulers[2] = - \
            np.degrees(np.arctan2(-self_to_camera[1], self_to_camera[0]))
        dist2d = pyrr.vector.length(self_to_camera)
        self.eulers[1] = -np.degrees(np.arctan2(self_to_camera[2], dist2d))




UNIT_ID_TO_CLASS = {ENTITY_TYPE["UNIT_TRIANGLE"]: Unit_Triangle,
                ENTITY_TYPE["UNIT_CUBE"]: Unit_Cube,
                ENTITY_TYPE["UNIT_DEFAULT"]:Unit_Default,
                }

