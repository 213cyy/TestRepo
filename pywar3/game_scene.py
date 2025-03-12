from config import *

from unit.cube.cube_default import *
from unit.no_unit.no_unit_default import *

PLAYER_COLORS = [
             np.array([0,13/255,107/255], dtype = np.float32),
             np.array([156/255,25/255,224/255], dtype = np.float32),
             np.array([255/255,93/255,162/255], dtype = np.float32),
             np.array([255/255,162/255,93/255], dtype = np.float32),
             np.array([153/255,221/255,204/255], dtype = np.float32),
             np.array([255/255,93/255,93/255], dtype = np.float32),
             np.array([93/255,255/255,93/255], dtype = np.float32),
        ]

palette = {
            "Navy": np.array([0,13/255,107/255], dtype = np.float32),
            "Purple": np.array([156/255,25/255,224/255], dtype = np.float32),
            "Pink": np.array([255/255,93/255,162/255], dtype = np.float32),
            "Orange": np.array([255/255,162/255,93/255], dtype = np.float32),
            "Teal": np.array([153/255,221/255,204/255], dtype = np.float32),
            "Red": np.array([255/255,93/255,93/255], dtype = np.float32),
            "Green": np.array([93/255,255/255,93/255], dtype = np.float32),
        }

class GameManager:
    """
        Manages all objects and coordinates their interactions.
    """
    # __slots__ = ("entities", "player", "lights")

    def __init__(self):
        self.game_time = 0

        self.fun_once_list =[self.init_game]
        
        self.entities: dict[int, list] = {
            # ENTITY_TYPE["CUBE"]: [
            #     Cube(position = [6,0,1],  eulers = [0,0,0])],
            # ENTITY_TYPE["GROUND"]: [
            #     TileMap()
            # ],
            # ENTITY_TYPE["MEDKIT"]: [
            #     BillBoard(position = [3,0,0.5])
            # ]
        }
        self.unit_list = set()
        self.id_to_class={}
        self.id_to_engine = {}

    def register_unit_class(self,unit_class,unit_engine):
        name = unit_class.unit_class_id
        self.id_to_class[name] = unit_class
        self.id_to_engine[name] = unit_engine

    def update_with_input(self, keys_state, window_state):
        self.MVP = window_state['mvp']
        self.window_state = window_state
        for k in self.fun_once_list:
            k()
        self.fun_once_list = []
        self.game_time += window_state['frametime']
        self.update(window_state['frametime'])

    def update(self, window_state) -> None:
        for entity in self.unit_list:
            entity.update(window_state)
        


    def init_game(self):
        self.register_unit_class(UnitCube,CubeRenderEnigine())
        self.register_unit_class(UnitNone,CubeNoneRenderEnigine())

        self.CreateUnit(3,"cube",0,0,270)
        self.CreateUnit(2,"cube",256,256,45)
        self.CreateUnit(1,"none",-256,256,100)

        # self.CreateUnit(3,ENTITY_TYPE["UNIT_DEFAULT"],0,0,270)
        # self.CreateEntity(2,ENTITY_TYPE["UNIT_CUBE"],-50,0,0)
        # self.CreateEntity(1,ENTITY_TYPE["UNIT_TRIANGLE"],100,0,270)
        # self.CreateEntity(3,ENTITY_TYPE["UNIT_TRIANGLE"],0,100,270)
        # self.CreateEntity(4,ENTITY_TYPE["UNIT_TRIANGLE"],20,20,90)
        # self.CreateEntity(5,ENTITY_TYPE["UNIT_TRIANGLE"],40,0,0)


    def render(self):
        for engine in self.id_to_engine.values():
            engine.render(self.window_state)

    def destroy(self):
        for engine in self.id_to_engine.values():
            engine.destroy()

    def CreateEntity(self,player_id, unitid, x, y, face ):
        ClassName = UNIT_ID_TO_CLASS[unitid]
        u = ClassName(player_id, x, y, face)
        self.entities.setdefault(unitid, []).append(u)

    # CreateUnit takes player id, integer unitid, real x, real y, real face returns unit
    def CreateUnit(self,player_id, unitid, x, y, face ):
        position = np.array([x, y, 0], dtype=np.float32)
        eulers = np.deg2rad([0,face, 0], dtype=np.float32)
        color = PLAYER_COLORS[player_id]

        ClassName = self.id_to_class[unitid]
        # unit_class = type_tabel[unitid]
        u = ClassName(player_id,position,eulers,color)

        self.unit_list.add(u)
        self.id_to_engine[unitid].add_unit(u)

