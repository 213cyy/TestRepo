

class UnitDefault():
    unit_class_id = "unitdefault"

    def __init__(self, engine, player_id, position, eulers, color):
        self.render_engine = engine
        self.player_id = player_id
        self.position = position
        self.pos_origin_z = position[2]
        self.pos_origin_z = 100
        self.eulers = eulers
        self.color = color

        self.health_val = 200
        self.health_val_max = 200