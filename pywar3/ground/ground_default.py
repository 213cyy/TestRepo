from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from struct import unpack, iter_unpack, Struct
import numpy as np
from PIL import Image

if __name__ == "__main__":
    from conf import *
else:
    from ground.conf import *


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


class GroundRenderEngine:
    # default_MVP = np.array([[1.0,  0.0,  0.0,  0.0],
    #                         [0.0,  1.0,  0.0,  0.0],
    #                         [0.0,  0.0,  1.0,  0.0],
    #                         [0.0,  0.0,  0.0,  1.0]], dtype='f4')
    default_MVP = np.array([
        [1.0711e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00],
        [0.0000e+00,  1.1839e+00,  5.6278e-01,  5.5919e-01],
        [0.0000e+00,  7.9861e-01, -8.3436e-01, -8.2903e-01],
        [0.0000e+00, -8.7167e-05,  1.6284e+03,  1.6500e+03]
    ],  dtype=np.float32)

    def create_shader(self, vertex_filepath: str, fragment_filepath: str):

        with open(vertex_filepath, 'r') as f:
            vertex_src = f.readlines()
        with open(fragment_filepath, 'r') as f:
            fragment_src = f.readlines()
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))

        return shader

    def __init__(self):
        mapw3e = MapInfo()
        self.map_width = mapw3e.width
        self.map_height = mapw3e.height
        self.map_bottom_left_x = mapw3e.center_offset_x
        self.map_bottom_left_y = mapw3e.center_offset_y
        self.map_z_list = np.array(
            mapw3e.ground_z_list).reshape((mapw3e.width, -1))

        self.water_phase = 0
        shader_wireframe = self.create_shader(
            GROUND_SHADER_FOLDER + "wireframe.vert",
            GROUND_SHADER_FOLDER + "wireframe.frag")
        self.wireframe = GroundMesh_Frame(mapw3e, shader_wireframe)

        shader_terrain = self.create_shader(
            GROUND_SHADER_FOLDER + "terrain.vert",
            GROUND_SHADER_FOLDER + "terrain.frag")
        self.terrain = GroundMesh_Terrain(mapw3e, shader_terrain)

        shader_water = self.create_shader(
            GROUND_SHADER_FOLDER + "water.vert",
            GROUND_SHADER_FOLDER + "water.frag")
        self.water = GroundMesh_Water(mapw3e, shader_water)

        shader_cliff = self.create_shader(
            GROUND_SHADER_FOLDER + "cliff.vert",
            GROUND_SHADER_FOLDER + "cliff.frag")
        self.cliff = GroundMesh_Cliff(mapw3e, shader_cliff)

        self.MVP = self.default_MVP
        self.ubo_MVP = glGenBuffers(1)
        glBindBuffer(GL_UNIFORM_BUFFER, self.ubo_MVP)
        glBufferData(GL_UNIFORM_BUFFER, self.MVP.nbytes,
                     self.MVP, GL_STATIC_DRAW)
        glBindBufferBase(GL_UNIFORM_BUFFER, 0, self.ubo_MVP)

        corner_position_array = np.array(mapw3e.corner_point_array, dtype='f4')
        # corner_pos_buffer = glCreateBuffers(1)
        self.ubo_corner_pos = glGenBuffers(1)
        glBindBuffer(GL_UNIFORM_BUFFER, self.ubo_corner_pos)
        # glBufferData(GL_SHADER_STORAGE_BUFFER, corner_position_array.nbytes, corner_position_array, GL_STATIC_DRAW)
        # glNamedBufferStorage(cliff_level_buffer, width * height * sizeof(float), nullptr, GL_DYNAMIC_STORAGE_BIT)
        glBufferStorage(GL_UNIFORM_BUFFER, corner_position_array.nbytes,
                        corner_position_array, GL_DYNAMIC_STORAGE_BIT)
        glBindBufferBase(GL_UNIFORM_BUFFER, 1, self.ubo_corner_pos)

    def render(self, view=None, projection=None):
        self.wireframe.render()
        self.terrain.render()
        self.cliff.render()
        self.water.render(self.water_phase)

    def destroy(self) -> None:
        self.wireframe.destroy()
        self.terrain.destroy()
        self.water.destroy()
        self.cliff.destroy()

    def update_with_input(self, keys_state, window_state):
        MVP = window_state['mvp']
        glBindBuffer(GL_UNIFORM_BUFFER, self.ubo_MVP)
        glBufferData(GL_UNIFORM_BUFFER, MVP.nbytes, MVP, GL_STATIC_DRAW)
        # glBindBuffer(GL_UNIFORM_BUFFER, 0)

        self.water_phase += window_state['frametime']
        # print(self.water_phase)

    def get_position_height(self, postion):
        pos_x, pos_y = postion[0], postion[1]
        quot_width, dx = divmod(pos_x - self.map_bottom_left_x, 128)
        quot_height, dy = divmod(pos_y - self.map_bottom_left_y, 128)
        ind_width = int(quot_width)
        ind_height = int(quot_height)
        b1 = self.map_z_list[ind_height][ind_width]
        b2 = self.map_z_list[ind_height][ind_width+1]
        t1 = self.map_z_list[ind_height+1][ind_width]
        t2 = self.map_z_list[ind_height+1][ind_width+1]
        bottom_z = (1-dx/128)*b1 + dx/128*b2
        top_z = (1-dx/128)*t1 + dx/128*t2
        pos_z = (1-dy/128)*bottom_z + dy/128*top_z
        return pos_z


class GroundMesh_Frame:
    def __init__(self, mapw3e, shader) -> None:
        self.shader = shader

        self.width_n = width_n = mapw3e.width
        self.height_n = height_n = mapw3e.height
        row_start = list(range(0, height_n*width_n, width_n))
        row_stride = [1] * height_n
        row_color = [1, 0, 0, 0] * (height_n//4) + [1]
        col_start = list(range(0, width_n))
        col_stride = [width_n] * width_n
        col_color = [1, 0, 0, 0] * (width_n//4) + [1]

        temp_array = np.dstack((row_start+col_start,
                                row_stride + col_stride,
                                row_color+col_color))

        line_attr_array = temp_array.flatten().astype('u4')
        # line_attr_buffer = glCreateBuffers(1)
        self.line_attr_buffer = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.line_attr_buffer)
        # glBufferData(GL_SHADER_STORAGE_BUFFER, line_attr_array.nbytes, line_attr_array, GL_STATIC_DRAW)
        # glNamedBufferStorage(cliff_level_buffer, width * height * sizeof(float), nullptr, GL_DYNAMIC_STORAGE_BIT)
        glBufferStorage(GL_SHADER_STORAGE_BUFFER, line_attr_array.nbytes,
                        line_attr_array, GL_DYNAMIC_STORAGE_BIT)

        # for glDrawArraysInstanced execution
        # To run glDrawArraysInstanced without encountering an exception,
        # we should provide a 'vao' if we haven't done so already
        self.vao_dummy = glGenVertexArrays(1)
        glBindVertexArray(self.vao_dummy)

        self.line_attr_offset_location = 0

    def render(self,):
        glUseProgram(self.shader)

        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 2, self.line_attr_buffer)

        glUniform1ui(self.line_attr_offset_location, 0)
        glDrawArraysInstanced(GL_LINE_STRIP, 0, self.width_n, self.height_n)

        glUniform1ui(self.line_attr_offset_location, self.height_n)
        glDrawArraysInstanced(GL_LINE_STRIP, 0, self.height_n, self.width_n)

    def destroy(self) -> None:
        glDeleteProgram(self.shader)
        glDeleteBuffers(2, (self.line_attr_buffer, self.vao_dummy))


class GroundMesh_Terrain:
    def __init__(self, mapw3e, shader) -> None:
        self.shader = shader

        self.ground_tex = TileTexture(mapw3e.ground_tileset_ids)

        ground_tile_index = np.array(mapw3e.tile_ground_array, dtype='u4')
        self.instancecount = int(ground_tile_index.size/6)

        self.ground_index_buffer = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.ground_index_buffer)
        glBufferStorage(GL_SHADER_STORAGE_BUFFER, ground_tile_index.nbytes,
                        ground_tile_index, GL_DYNAMIC_STORAGE_BIT)

        self.groundtile_inst_buffer = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.groundtile_inst_buffer)
        groundtile_tex_index = np.array(mapw3e.tile_ground_inst, dtype='u4')
        glBufferStorage(GL_SHADER_STORAGE_BUFFER, groundtile_tex_index.nbytes,
                        groundtile_tex_index, GL_DYNAMIC_STORAGE_BIT)
        # glBufferData(GL_SHADER_STORAGE_BUFFER, line_attr_array.nbytes, line_attr_array, GL_STATIC_DRAW)

        # for glDrawArraysInstanced execution
        # To run glDrawArraysInstanced without encountering an exception,
        # we should provide a 'vao' if we haven't done so already
        self.vao_dummy = glGenVertexArrays(1)
        glBindVertexArray(self.vao_dummy)
        glBindVertexArray(0)

    def render(self):
        glUseProgram(self.shader)
        self.ground_tex.use()

        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 2, self.ground_index_buffer)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 3,
                         self.groundtile_inst_buffer)
        # glBindVertexArray(self.vao_dummy)
        glDrawArraysInstanced(GL_TRIANGLES, 0, 6, self.instancecount)

    def destroy(self):
        glDeleteProgram(self.shader)
        self.ground_tex.destroy()
        glDeleteVertexArrays(1, (self.vao_dummy,))
        glDeleteBuffers(2, (self.ground_index_buffer,
                        self.groundtile_inst_buffer))


class GroundMesh_Water:
    def __init__(self, mapw3e, shader) -> None:
        self.shader = shader
        self.water_tex = WaterTexture()

        water_tile_index = np.array(mapw3e.tile_water_array, dtype='u4')
        self.instancecount = int(water_tile_index.size/6)

        self.water_index_buffer = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.water_index_buffer)
        glBufferStorage(GL_SHADER_STORAGE_BUFFER, water_tile_index.nbytes,
                        water_tile_index, GL_DYNAMIC_STORAGE_BIT)

        self.watertile_phase_buffer = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.watertile_phase_buffer)
        watertile_init_phase = np.random.randint(
            0, WATER_TEXTURES_NUM, self.instancecount, dtype='u4')
        glBufferStorage(GL_SHADER_STORAGE_BUFFER, watertile_init_phase.nbytes,
                        watertile_init_phase, GL_DYNAMIC_STORAGE_BIT)
        # glBufferData(GL_SHADER_STORAGE_BUFFER, line_attr_array.nbytes, line_attr_array, GL_STATIC_DRAW)

        # for glDrawArraysInstanced execution
        # To run glDrawArraysInstanced without encountering an exception,
        # we should provide a 'vao' if we haven't done so already
        self.vao_dummy = glGenVertexArrays(1)
        glBindVertexArray(self.vao_dummy)

        glBindVertexArray(0)
        self.water_phase_location = 2

    def render(self, water_phase):
        glUseProgram(self.shader)
        self.water_tex.use()
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 2, self.water_index_buffer)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 3,
                         self.watertile_phase_buffer)

        # glBindVertexArray(self.vao_dummy)
        water_phase_index = int(water_phase/67 % WATER_TEXTURES_NUM)
        # print(water_phase_index)

        glUniform1ui(self.water_phase_location, water_phase_index)
        glDrawArraysInstanced(GL_TRIANGLES, 0, 6, self.instancecount)

    def destroy(self):
        glDeleteProgram(self.shader)
        self.water_tex.destroy()
        glDeleteVertexArrays(1, (self.vao_dummy,))
        glDeleteBuffers(2, (self.water_index_buffer,
                        self.watertile_phase_buffer))


class GroundMesh_Cliff:

    def __init__(self, mapw3e, shader) -> None:
        self.shader = shader
        self.cliff_tex = CliffTexture()

        import importlib.util
        file_path = CLIFF_TEXTURE_FOLDER + 'cliff_data.py'
        # Load the module
        spec = importlib.util.spec_from_file_location('temp_module', file_path)
        module_data = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module_data)

        Vertices_16 = module_data.Vertices_16
        TVertices_16 = module_data.TVertices_16
        Triangles = module_data.Triangles

        v_16 = np.array(Vertices_16)
        # vert = np.array(Vertices_16, dtype=np.float32)
        vert = np.c_[v_16[:, 1], -v_16[:, 0], v_16[:, 2]].astype('f4')
        vert_uv = np.array(TVertices_16, dtype=np.float32)
        vertices = np.hstack((vert, vert_uv)).ravel()

        self.vertex_count = len(Vertices_16)
        self.indices_count = len(Triangles)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes,
                     vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE,
                              20, ctypes.c_void_p(12))

        self.ebo = glGenBuffers(1)
        indices = np.array(Triangles, dtype=np.uint32)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                     indices.nbytes, indices, GL_STATIC_DRAW)

        glBindVertexArray(0)

        cliff_tile_index = np.array(mapw3e.tile_cliff_inst, dtype='u4')
        self.instancecount = int(cliff_tile_index.size)

        self.water_index_buffer = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.water_index_buffer)
        glBufferStorage(GL_SHADER_STORAGE_BUFFER, cliff_tile_index.nbytes,
                        cliff_tile_index, GL_DYNAMIC_STORAGE_BIT)

        self.width_stride = mapw3e.width
        self.width_stride_location = 2

    def render(self) -> None:
        glUseProgram(self.shader)
        self.cliff_tex.use()
        # glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, self.corner_pos_buffer)
        glBindVertexArray(self.vao)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 2, self.water_index_buffer)
        glUniform1ui(self.width_stride_location, int(self.width_stride))

        # glDrawElements(GL_TRIANGLES, self.indices_count, GL_UNSIGNED_INT,ctypes.c_void_p(0))
        # glDrawElementsInstanced(GL_TRIANGLES, indices, GL_UNSIGNED_SHORT, nullptr, static_cast<int>(render_jobs.size()))

        glDrawElementsInstanced(GL_TRIANGLES, self.indices_count,
                                GL_UNSIGNED_INT, ctypes.c_void_p(0), self.instancecount)
        # glDrawArraysInstanced(GL_TRIANGLES, 0, 6, self.indices_count)

    def destroy(self) -> None:
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(2, (self.vbo, self.ebo))


class TileTexture:

    tile_size = 64
    lods = 7  # log2(64) + 1
    image_width = 512
    image_height = 256

    def __init__(self, tileset_ids: list):

        self.textures = glGenTextures(len(tileset_ids))
        tex_color = []
        for tex_id, tileset_id in zip(self.textures, tileset_ids):
            filepath = TILESET_ID_TO_FILENAME[tileset_id]
            with Image.open(filepath, mode="r") as img:
                # image_width,image_height = img.size
                # img = img.convert("RGBA")
                # img_data = img.tobytes()
                img_format = GL_RGB if img.mode == "RGB" else GL_RGBA
                sized_format = GL_RGB8 if img.mode == "RGB" else GL_RGBA8

                # self.texture = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D_ARRAY, tex_id)
                glTexStorage3D(GL_TEXTURE_2D_ARRAY, self.lods, sized_format,
                               64, 64, 32)
                glTexParameteri(GL_TEXTURE_2D_ARRAY,
                                GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
                glTexParameteri(GL_TEXTURE_2D_ARRAY,
                                GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
                glTexParameteri(GL_TEXTURE_2D_ARRAY,
                                GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
                # glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

                FLIP_TOP_BOTTOM = 1
                xx, yy = np.meshgrid(range(0, 512, 64), range(0, 256, 64))
                ind_sub = np.arange(16).reshape(4, -1)
                index = np.hstack((ind_sub, ind_sub+16))
                for x, y, ind in zip(xx.ravel(), yy.ravel(), index.ravel()):
                    #     print(a,b,c)

                    # for ind in range(32):
                    #     x, y = divmod(ind, 4)
                    #     xx, yy = 64*x, 64*y
                    img_ = img.crop((x, y, x+64, y+64)
                                    ).transpose(method=FLIP_TOP_BOTTOM)
                    img_data = img_.tobytes()
                    # img.show()
                    # glTexSubImage3D(target,level,xoffset,yoffset,zoffset,width,height,depth,format,type,pixels)
                    glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0,
                                    0, 0, ind, 64, 64, 1,
                                    img_format, GL_UNSIGNED_BYTE, img_data)

                # glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
                # glTexImage3D(target,level,internalformat,width,height,depth,border,format,type,pixels)
                # glTexImage3D(GL_TEXTURE_2D_ARRAY, 0, img_format,
                #         64, 64, 32, 0, img_format, GL_UNSIGNED_BYTE, img.tobytes())

            glGenerateMipmap(GL_TEXTURE_2D_ARRAY)
            img_bytes = glGetTexImage(GL_TEXTURE_2D_ARRAY,
                                      6, img_format, GL_UNSIGNED_BYTE)
            tex_color.append(img_bytes[:3])

        self.tex_color_bytes = tex_color

    def texture_color_each_levels(self, tex_index):
        # for check and dubug
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.textures[tex_index])

        for level in range(7):
            ww = int(512/2**level)
            hh = int(256/2**level)
            img_bytes = glGetTexImage(
                GL_TEXTURE_2D_ARRAY, level, GL_RGB, GL_UNSIGNED_BYTE)
            # img_back = Image.frombytes("RGB", (ww,hh), img_bytes)
            # img_back.show()
            print(img_bytes[:3].hex())

    def __init__GL4_5(self, tileset_ids):
        img = None
        width = self.image_width
        tile_size = self.tile_size
        # glCreateTextures(GL_TEXTURE_2D_ARRAY, len(tileset_ids), &id)
        for tex_id in self.textures:
            channels = 3 if img.mode == "RGB" else 4
            pixel_format = GL_RGB if img.mode == "RGB" else GL_RGBA
            bit_format = GL_RGB8 if img.mode == "RGB" else GL_RGBA8

            glTextureStorage3D(tex_id, self.lods, bit_format,
                               tile_size, tile_size, 32)
            glTextureParameteri(tex_id, GL_TEXTURE_MIN_FILTER,
                                GL_LINEAR_MIPMAP_LINEAR)
            glTextureParameteri(tex_id, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTextureParameteri(tex_id, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

            data = img.tobytes()
            glPixelStorei(GL_UNPACK_ROW_LENGTH, width)
            for y in range(4):
                for x in range(4):
                    glTextureSubImage3D(id, 0, 0, 0, y * 4 + x, tile_size, tile_size, 1, pixel_format,
                                        GL_UNSIGNED_BYTE, data + (y * tile_size * width + x * tile_size) * channels)
                    glTextureSubImage3D(id, 0, 0, 0, y * 4 + x + 16, tile_size, tile_size, 1, pixel_format,
                                        GL_UNSIGNED_BYTE, data + (y * tile_size * width + (x + 4) * tile_size) * channels)

            glPixelStorei(GL_UNPACK_ROW_LENGTH, 0)
            glGenerateTextureMipmap(tex_id)

            minimap_color = 0
            glGetTextureSubImage(id, self.lods - 1, 0, 0, 0,
                                 1, 1, 1, format, GL_FLOAT, 16, minimap_color)
            minimap_color *= 255

    def use(self) -> None:
        for unit, texture in enumerate(self.textures):
            # glBindTextureUnit(GL_TEXTURE0 + unit, texture)
            glActiveTexture(GL_TEXTURE0 + unit)
            glBindTexture(GL_TEXTURE_2D_ARRAY, texture)

    def destroy(self) -> None:
        glDeleteTextures(len(self.textures), (*self.textures,))


class WaterTexture:
    # Water textures
    lods = 8  # log2(128) + 1
    image_width = image_height = 128

    def __init__(self,):
        # glCreateTextures(GL_TEXTURE_2D_ARRAY, 1, &water_texture_array)
        # glTextureStorage3D(water_texture_array, self.lods, GL_RGBA8, 128, 128, WATER_TEXTURES_NUM)
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.texture)
        glTexStorage3D(GL_TEXTURE_2D_ARRAY, self.lods, GL_RGBA8,
                       128, 128, WATER_TEXTURES_NUM)
        glTexParameteri(GL_TEXTURE_2D_ARRAY,
                        GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D_ARRAY,
                        GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        for index in range(WATER_TEXTURES_NUM):
            filepath = WATER_INDEX_TO_FILENAME(index)
            with Image.open(filepath, mode="r") as image:
                # image_width,image_height = image.size # for texture size check
                img = image.convert("RGBA")
                glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0,
                                0, 0, index, 128, 128, 1,
                                GL_RGBA, GL_UNSIGNED_BYTE, img.tobytes())

        glGenerateMipmap(GL_TEXTURE_2D_ARRAY)

    def use(self) -> None:
        # glBindTextureUnit(GL_TEXTURE0 + unit, texture)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.texture)

    def destroy(self) -> None:
        glDeleteTextures(1, (self.texture,))


class CliffTexture:

    # __slots__ = ("texture", "unit", "texture_type")

    def __init__(self):
        self.unit = 0
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                        GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        filepath = CLIFF_TEXTURE_FOLDER+"Cliff1.blp"
        with Image.open(filepath, mode="r") as img:
            image_width, image_height = img.size
            img = img.convert("RGBA")
            img_data = img.tobytes()
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width,
                         image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self) -> None:
        glActiveTexture(GL_TEXTURE0 + self.unit)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def destroy(self) -> None:
        glDeleteTextures(1, (self.texture,))


if __name__ == "__main__":
    print(10 * "-", "debug", 10 * "-")

    from conf import *
    from sys import path
    path.append(ROOT)

    from main import App
    my_app = App()

    my_app.game_manager.fun_once_list = []
    # key_engine = GroundRenderEngine
    # key_engine = QuadBoardRenderEngine
    # my_app.game_manager.register_agent_engine(
    #         key_engine(my_app.game_manager))
    # my_app.game_manager.CreateDestructable("quadboard", 200, 200, 0)
    # my_app.game_manager.CreateDestructable(
    #           key_engine.agent_class_name, 200, 200, 0)

    my_app.run()
    my_app.quit()
