
from .conf import * 
from struct import unpack, iter_unpack, Struct
import numpy as np
import os 
import itertools

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
        self.init_from_file()

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
        for row, col in itertools.product(range(height-1),range(width-1)):
            cbl = col+row*width
            tile_points = [corner_list[cbl],
                           corner_list[cbl+1],
                           corner_list[cbl+width],
                           corner_list[cbl+width+1]]

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
        for row, col in itertools.product(range(height-1),range(width-1)):
            cbl = col+row*width # 左下角
            ctl = cbl+width # 左上角
            tile_points = [
                corner_list[cbl+1],
                corner_list[cbl],
                corner_list[ctl+1],
                corner_list[ctl],
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
                self.tile_ground_array += [cbl, cbl+1, ctl, cbl+1, ctl+1, ctl]
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
                self.tile_water_array += [cbl, cbl+1, ctl, cbl+1, ctl+1, ctl]
                # self.tile_water_inst += [cbl]

        # ------------- third loop to populate corner_point_array ------------------
        # corner_point_array:
        # contains universal property (position + color) info for all corner points
        self.corner_point_array = []
        self.ground_z_list = []
        for index,(row, col) in enumerate(itertools.product(range(height),range(width))):
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
    # 生成 结构解析 字符串
    def gen_stu(self, stu):
        lstu = ''.join(stu.values()) if isinstance(stu, dict) \
                else stu if  isinstance(stu, str) \
                else ''.join(stu) if isinstance(stu,list) \
                else None
        if lstu is None:
            raise ValueError('stu must be a dict,string,or list')
        return lstu
    
    def load_fdata(self, fr, stu,  styp='bytes', rlen=None, rtyp = 'return', endian='='):
        '''
        说明:从文件中读取数据
        参数:
            fr: 文件对象
            stu: 结构解析字符串，可以是 字典, 字符串, 或列表
            styp: 结构解析类型, bytes: 单次结构解析, num_list: 数据中带元素个数的列表, list:  数据中不带元素个数的列表
            rtyp: 结果处理方式, return: 返回数据, init:初始化数据，init和字典组合，可以将数据直接转换为该对象的变量
            endian: 结构解析的字节序
        '''
        cinit = True if isinstance(stu, dict) else False
        
        if not cinit and rtyp == 'init':
            raise ValueError('stru must be a dict when rtyp is init')
        fr_unpack = lambda x: (lambda x:x.unpack(fr.read(x.size)))(
            Struct(endian+x)
        )
        fr_iter_unpack = lambda x,rlen=None: (lambda x,rlen:x.iter_unpack(fr.read(rlen)))(
            Struct(endian+x),rlen
        )
        if styp == 'bytes':
            data = fr_unpack(self.gen_stu(stu))
        elif styp == 'num_list':
            length = fr_unpack(stu.pop('num_'))
            data = fr_unpack(self.gen_stu(stu)*length[0])
        elif styp == 'list':
            data = fr_iter_unpack(self.gen_stu(stu),None)
        else:
            raise ValueError('styp must be bytes,num_list,list')
        
        if rtyp == 'return':
            return data
        elif rtyp == 'init':
            if styp in ['num_list','list'] and len(stu)==1:
                ds = []
                for v in data:
                    ds.append(v.decode() if isinstance(v, bytes) else v)
                setattr(self, list(stu.keys())[0], ds)
                return 
            
            for key, value in zip(stu.keys(), data):
                value = value.decode() if isinstance(value, bytes) else value
                setattr(self, key, value)
        else:
            raise ValueError('rtyp must be return or init')

    def init_from_file(self, w3eFilepath=None):
        w3eFilepath = WAR3_ENVIRONMENT_FILE
        # https://867380699.github.io/blog/2019/05/09/W3X_Files_Format#war3mapw3e
        print('init_from_file:', w3eFilepath, os.path.getsize(w3eFilepath))
        with open(w3eFilepath, 'rb') as fr:
            self.load_fdata(fr, {"file_id":'4s', "version":'I', "tileset_id":'c', "custom_tilesets":'I'},rtyp='init')
            self.load_fdata(fr, {'num_':'I','ground_tileset_ids':'4s'}, styp='num_list', rtyp='init')
            self.load_fdata(fr, {'num_':'I','cliff_tileset_ids':'4s'}, styp='num_list', rtyp='init')
            self.load_fdata(fr, {"width":'I', "height":'I', "center_offset_x":'f', "center_offset_y":'f'},rtyp='init')
            self.corner_list = [TileCorner(k) for k in self.load_fdata(fr, 'HHBBB', styp='list', rtyp='return')]