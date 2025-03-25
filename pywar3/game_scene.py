from config import *

from units.cube.cube_default import *
from units.nounit.no_unit import *
from doodad.quadboard.quad_board import *
from effects.statebar.state_bar import *

PLAYER_COLORS = [
    np.array([0, 13/255, 107/255], dtype=np.float32),
    np.array([156/255, 25/255, 224/255], dtype=np.float32),
    np.array([255/255, 93/255, 162/255], dtype=np.float32),
    np.array([255/255, 162/255, 93/255], dtype=np.float32),
    np.array([153/255, 221/255, 204/255], dtype=np.float32),
    np.array([255/255, 93/255, 93/255], dtype=np.float32),
    np.array([93/255, 255/255, 93/255], dtype=np.float32),
]

palette = {
    "Navy": np.array([0, 13/255, 107/255], dtype=np.float32),
    "Purple": np.array([156/255, 25/255, 224/255], dtype=np.float32),
    "Pink": np.array([255/255, 93/255, 162/255], dtype=np.float32),
    "Orange": np.array([255/255, 162/255, 93/255], dtype=np.float32),
    "Teal": np.array([153/255, 221/255, 204/255], dtype=np.float32),
    "Red": np.array([255/255, 93/255, 93/255], dtype=np.float32),
    "Green": np.array([93/255, 255/255, 93/255], dtype=np.float32),
}


class GameManager:

    def __init__(self, window_info):
        self.window_info = window_info
        self.game_time = 0

        self.fun_once_list = [self.init_game]

        self.agent_group = set()
        self.unit_group = set()
        self.id_to_class = {}
        self.id_to_engine = {}

    def register_agent_engine(self, agent_engine):
        name = agent_engine.agent_class_name
        # self.id_to_class[name] = unit_class
        self.id_to_engine[name] = agent_engine

    def update_with_input(self, keys_state, window_state):
        self.MVP = window_state['mvp']
        self.window_state = window_state
        for k in self.fun_once_list:
            k()
        self.fun_once_list = []
        self.game_time += window_state['frametime']
        self.update(window_state['frametime'])

    def update(self, window_state) -> None:
        for entity in self.unit_group:
            entity.update(window_state)

    def init_game(self):
        self.register_agent_engine(CubeRenderEngine(self))
        self.register_agent_engine(CubeNoneRenderEngine(self))
        self.register_agent_engine(QuadBoardRenderEngine(self))
        self.register_agent_engine(StateBarRenderEngine(self))

        u = self.CreateUnit(3, "cube", 0, 0, 270)
        self.UnitAddAbility(u, "statebar")
        u = self.CreateUnit(2, "cube", 256, 256, 45)
        self.UnitAddAbility(u, "statebar")
        u = self.CreateUnit(1, "none_unit", -256, 256, 100)
        self.UnitAddAbility(u, "statebar")

        self.CreateDestructable("quadboard", 200, 200, 0)
        self.CreateDestructable("quadboard", 400, 200, 0, 2)
        self.CreateDestructable("quadboard", 400, 600, 0, 1.5)
        # self.CreateUnit(3,ENTITY_TYPE["UNIT_DEFAULT"],0,0,270)
        # self.CreateEntity(2,ENTITY_TYPE["UNIT_CUBE"],-50,0,0)
        # self.CreateEntity(1,ENTITY_TYPE["UNIT_TRIANGLE"],100,0,270)

    def render(self):
        for engine in self.id_to_engine.values():
            engine.render(self.window_state)

    def destroy(self):
        for engine in self.id_to_engine.values():
            engine.destroy()

    # CreateUnit takes
    # player id, integer unitid, real x, real y, real face
    # returns unit
    def CreateUnit(self, player_id, unitid, x, y, face):
        position = np.array([x, y, 0], dtype=np.float32)
        eulers = np.deg2rad([0, face, 0], dtype=np.float32)
        color = PLAYER_COLORS[player_id]

        engine = self.id_to_engine[unitid]
        u = engine.create_agent(player_id, position, eulers, color)
        self.unit_group.add(u)

        return u

    # CreateDestructable takes
    # integer objectid, real x, real y, real face, real scale, integer variation
    # returns destructable
    def CreateDestructable(self, objectid, x, y, face, scale=1, variation=0):
        position = np.array([x, y, 0], dtype=np.float32)
        eulers = np.deg2rad([0, face, 0], dtype=np.float32)

        engine = self.id_to_engine[objectid]
        d = engine.create_agent(position, eulers, scale, variation)
        self.unit_group.add(d)

        return d

    # UnitAddAbility takes
    # unit whichUnit, integer abilityId
    # returns boolean
    def UnitAddAbility(self, whichUnit, abilityId):
        engine = self.id_to_engine[abilityId]
        a = engine.create_agent(whichUnit)
        self.unit_group.add(a)

        return a
