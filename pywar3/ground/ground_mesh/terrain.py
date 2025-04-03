from OpenGL.GL import *
from PIL import Image
import numpy as np
from .mesh import Mesh
from ..conf import *

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


class Terrain(Mesh):
    def __init__(self, mapw3e, vert, frag) -> None:
        self.shader = self.create_shader(vert, frag)

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
