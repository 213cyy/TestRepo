
from .conf import * 
from struct import unpack, iter_unpack, Struct
import numpy as np

class TileCorner:
    def __init__(self, tilepoint):

        # https://867380699.github.io/blog/2019/05/09/W3X_Files_Format#war3mapw3e
        self.ground_height = tilepoint[0]
        self.map_boundary_flag = tilepoint[1] & 0xC000 > 0
        self.water_height = tilepoint[1] & 0x3FFF
        self.camera_boundary_flag = tilepoint[2] & 0x80 > 0
        self.water_flag = tilepoint[2] & 0x40 > 0
        self.blight_flag = tilepoint[2] & 0x20 > 0
        self.ramp_flag = tilepoint[2] & 0x10 > 0
        self.tileset_type = tilepoint[2] & 0xf
        self.tile_var_raw = tilepoint[3] & 0x1f
        self.cliff_var = tilepoint[3] >> 5
        self.cliff_type = tilepoint[4] >> 4
        self.layer_level = tilepoint[4] & 0xf

        if self.tile_var_raw == 16:
            self.tile_var = 15
        elif self.tile_var_raw < 16:
            self.tile_var = self.tile_var_raw+16
        else:
            self.tile_var = 0

        self.ramp_level = -10
        self.cliff_flag = False

    def init_position(self, x, y):
        self.pos_x = x
        self.pos_y = y

        # ------------- final ground height ------------------
        # 0x2000 is the "ground zero"
        z1 = (self.ground_height - 0x2000) / 4
        # 2 is the "layer zero" level and "0x0200" the layer height
        z2 = (self.layer_level - 2) * 0x0200 / 4
        z3 = 0x0200 / 8 if self.cliff_flag and self.ramp_flag else 0
        self.pos_ground_z = z1+z2+z3

        # ------------- water ------------------
        self.pos_water_z = (self.water_height - 0x2000)/4 - 89.6

        # WATER_MINDEPTH=10
        # WATER_DEEPLEVEL=64
        # WATER_MAXDEPTH=72
        if self.water_flag:
            water_depth = np.clip(
                self.pos_water_z - self.pos_ground_z, WATER_MINDEPTH, WATER_MAXDEPTH)
            if water_depth <= WATER_DEEPLEVEL:
                value = (water_depth - WATER_MINDEPTH) / \
                    (WATER_DEEPLEVEL - WATER_MINDEPTH)
                water_color = WATER_SHALLOW_COLOR_MAX * np.array(value) \
                    + WATER_SHALLOW_COLOR_MIN * np.array(1 - value)
            else:
                value = (water_depth - WATER_DEEPLEVEL) / \
                    (WATER_MAXDEPTH - WATER_DEEPLEVEL)
                water_color = WATER_DEEP_COLOR_MAX * np.array(value) \
                    + WATER_DEEP_COLOR_MIN * np.array(1 - value)
        else:
            water_color = np.zeros(4)
        self.water_color = (water_color/255).tolist()

class MapInfo:
    def __init__(self, filename=None) -> None:
        self.load_file_data()

        corner_list = self.corner_list
        width = self.width
        height = self.height
        self.tile_ground_array = []
        self.tile_ground_inst = []
        # self.tile_cliff_array = []
        self.tile_cliff_inst = []
        self.tile_water_array = []
        # self.tile_water_inst = []

        # ------------- first loop to set cliff_flag ------------------
        # find and mark all cliff corner
        for index in range((height-1) * (width-1)):
            row, col = divmod(index, width-1)
        # for row in range(height-1):
        #     for col in range(width-1):
            corner_bottom_left = cbl = col+row*width
            corner_bottom_right = cbr = col+row*width+1
            corner_top_left = ctl = col+row*width+width
            corner_top_right = ctr = col+row*width+width+1
            tile_points = [corner_list[corner_bottom_left],
                           corner_list[corner_bottom_right],
                           corner_list[corner_top_left],
                           corner_list[corner_top_right]]

            tile_points_layer = [k.layer_level for k in tile_points]
            level_max = max(tile_points_layer)
            level_min = min(tile_points_layer)
            level_diff = level_max - level_min

            if level_diff > 0:
                for k in range(4):
                    if tile_points[k].ramp_flag:
                        if tile_points_layer[k] == level_min:
                            tile_points[k].cliff_flag = True
                    else:
                        tile_points[k].tileset_type = 4

        # ------------- second loop to populate  ------------------
        for index in range((height-1) * (width-1)):
            row, col = divmod(index, width-1)
        # for row in range(height-1):
        #     for col in range(width-1):
            corner_bottom_left = cbl = col+row*width
            corner_bottom_right = cbr = col+row*width+1
            corner_top_left = ctl = col+row*width+width
            corner_top_right = ctr = col+row*width+width+1
            tile_points = [
                corner_list[corner_bottom_right],
                corner_list[corner_bottom_left],
                corner_list[corner_top_right],
                corner_list[corner_top_left],
            ]

            # ------------- cliff ------------------
            ramp_count = sum([k.ramp_flag for k in tile_points])
            ramp_cliff_count = sum([k.cliff_flag for k in tile_points])

            tile_points_layer = [k.layer_level for k in tile_points]
            level_max = max(tile_points_layer)
            level_min = min(tile_points_layer)
            level_diff = level_max - level_min

            # ------------- cliff ------------------
            if ramp_count == 2 and ramp_cliff_count == 1:
                self.tile_cliff_inst += [cbl]
            elif level_diff > 0 and ramp_count != 4:
                self.tile_cliff_inst += [cbl]
            else:
                # ------------- ground ------------------
                self.tile_ground_array += [cbl, cbr, ctl, cbr, ctr, ctl]
                ground_var = corner_list[cbl].tile_var
                # print(ground_var)
                ground_types = [k.tileset_type for k in tile_points]
                type_list = sorted(set(ground_types))

                temp = [type_list[0] + (ground_var << 5)]
                for tp in type_list[1:]:
                    vary = sum(1 << i for i, gt in enumerate(
                        ground_types) if gt == tp)
                    temp.append(tp + (vary << 5))
                while len(temp) < 4:
                    temp.append(0x1f)

                # print(temp)
                self.tile_ground_inst.extend(temp)

            # ------------- water ------------------
            tile_points_water = [k.water_flag for k in tile_points]
            if any(tile_points_water):
                self.tile_water_array += [cbl, cbr, ctl, cbr, ctr, ctl]
                # self.tile_water_inst += [cbl]

        # ------------- third loop to populate corner_point_array ------------------
        # corner_point_array:
        # contains universal property (position + color) info for all corner points
        self.corner_point_array = []
        self.ground_z_list = []
        for index in range(height * width):
            row, col = divmod(index, width)
            pos_x = col * 128 + self.center_offset_x
            pos_y = row * 128 + self.center_offset_y
            corner_list[index].init_position(pos_x, pos_y)

            pos_ground_z = corner_list[index].pos_ground_z
            pos_water_z = corner_list[index].pos_water_z
            water_color = corner_list[index].water_color
            # print(water_color)
            self.corner_point_array += [pos_x, pos_y,
                                        pos_ground_z, pos_water_z] + water_color
            self.ground_z_list += [pos_ground_z]
        pass

    def load_file_data(self, w3eFilepath=None):

        w3eFilepath = WAR3_ENVIRONMENT_FILE
        with open(w3eFilepath, 'rb') as file:
            data = file.read()
        # print(len(data))

        # https://867380699.github.io/blog/2019/05/09/W3X_Files_Format#war3mapw3e
        head0 = Struct("=4sIcI")

        for key, value in zip(
            ("file_id", "version", "tileset_id", "custom_tilesets"),
                head0.unpack(data[0:head0.size])):
            setattr(self, key, value)
        # magic_number = W3E!
        # format_version = 11
        # main_tileset = L (Lordaeron Summer)

        p = head0.size
        ground_tileset_ids_count = unpack("I", data[p:p+4])[0]

        p = p+4
        temp_count = 4*ground_tileset_ids_count
        temp_bin = data[p:p+temp_count].decode()
        self.ground_tileset_ids = [temp_bin[ind:ind+4]
                                   for ind in range(0, temp_count, 4)]

        p = p+4*ground_tileset_ids_count
        cliff_tileset_ids_count = unpack("I", data[p:p+4])[0]
        p = p+4
        self.cliff_tileset_ids = iter_unpack(
            "4s", data[p:p+4*cliff_tileset_ids_count])
        p = p+4*cliff_tileset_ids_count

        head_end = Struct("IIff")
        for key, value in zip(
            ("width", "height", "center_offset_x", "center_offset_y"),
                head_end.unpack(data[p:p+head_end.size])):
            setattr(self, key, value)

        p = p+head_end.size
        # print(len(data[p:]))
        # corner_list_bin = data[p:]
        corner_list_raw = list(iter_unpack("HHBBB", data[p:]))
        # return list(iter_unpack("HHBBB", data[p:]))
        self.corner_list = [TileCorner(k) for k in corner_list_raw]
