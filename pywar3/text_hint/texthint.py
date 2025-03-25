from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import numpy as np
import time
from PIL import Image, ImageFont, ImageDraw

if __name__ == "__main__":
    from conf import *
else:
    from text_hint.conf import *


class TextBoxManager():
    default_back_color = [0.5, 0.9, 1.0]

    def __init__(self, auto_update=False,) -> None:
        self.auto_update_flag = auto_update
        self.text_box_list: list[TextBox] = []
        self.current_screen_size = (0, 0)
        self.frametime = 0
        self.renderer = TextBoxEngine()

        if auto_update:
            self.auto_update_last_time = time.time()

    def update_with_input(self, keys_state, window_state):
        self.frametime = window_state['frametime']
        width, height = window_state['windows_size']
        w, h = self.current_screen_size
        if width != w or height != h:
            self.update_with_screen_resize(width, height)
            self.current_screen_size = (width, height)

        if self.auto_update_flag:
            self.update_auto()
        else:
            self.update()

    def render(self):
        self.renderer.render(self.text_box_list)

    ## ## #################

    def update_auto(self):
        hint_type_list = ["ability_hint" ,"game_hint", "chat_hint","unit_hint"]

        current_time = time.time()
        dt_delay = current_time - self.auto_update_last_time
        if dt_delay > 2:
            current_type = hint_type_list[np.random.randint(4)]

            if all(k.message_type != current_type  for k in self.text_box_list ) :
                tbox = TextBox(self, current_type)
            else :
                tbox = TextBox(self, "unit_hint")

            self.text_box_list.append(tbox)
            self.auto_update_last_time = current_time

        self.update()

    def update(self):
        for k in self.text_box_list:
            k.update()

    def update_with_mouse(self, mouse_stat):
        pass

    def update_with_keyboard(self, key_stat):
        pass

    def update_with_screen_resize(self, width, height):
        for k in self.text_box_list:
            # k.update_with_screen_resize(width, height)
            k.destroy()

        self.text_box_list = []

    def destroy(self):
        self.renderer.destroy()
        for k in self.text_box_list:
            k.destroy()


class TextBox():
    vertices = (
        0, -1, 0, 0,
        1, -1, 1, 0,
        0, 0, 0, 1,
        1, -1, 1, 0,
        1, 0, 1, 1,
        0, 0, 0, 1,
    )
    vertices_raw = np.array(vertices).reshape((-1, 4))

    def generate_texture_image(self, font_size=16):
        if not font_size:
            scr_w, scr_h = self.manager.current_screen_size
            font_size = int(scr_w * scr_h / 12800)

        # fnt = ImageFont.truetype("arial.ttf", font_size)
        fnt = ImageFont.truetype("msyh.ttf", font_size)
        # fnt = ImageFont.truetype("symbol.ttf", font_size)
        # fnt = ImageFont.truetype("tahoma.ttf", font_size)

        if self.message_type == 'unit_hint':
            self.message_pos = np.random.uniform(-0.8, 0.8, size=2)
            canvas_size = (400, 200)
            canvas_start = (20, 20)
            if not self.message_str:
                msg_str = "Gold Mine\nGold: 12500"
            else:
                msg_str = self.message_str

            image = Image.new("RGBA", canvas_size, (30, 30, 30, 30))
            img_drawer = ImageDraw.Draw(image)

            #  ,align="center" align = "left",
            img_drawer.multiline_text(canvas_start, msg_str, font=fnt,
                                        fill=(255, 255, 255, 255))
            bbox = img_drawer.multiline_textbbox(
                                        canvas_start, msg_str, font=fnt, )
            bbox_extend = [bbox[0]-10, bbox[1]-10, bbox[2]+10, bbox[3]+10]
            img_drawer.rounded_rectangle(
                bbox_extend, radius=10, fill=None, outline=(243, 193, 44, 255), width=2)
            bbox_border = [bbox[0]-11, bbox[1]-11, bbox[2]+12, bbox[3]+12]

        elif self.message_type == 'ability_hint':
            self.message_pos = (0.21, -0.46)
            canvas_size = (450, 200)
            canvas_start = (20, 20)
            if not self.message_str:
                msg_str = '''Orders your units to move to the target area, while 
                    ignoring enemy units and attacks. Issuing a move order onto a 
                    target unit will cause your unit to follow the target.'''
            else:
                msg_str = self.message_str

            image = Image.new("RGBA", canvas_size, (30, 30, 30, 0))
            img_drawer = ImageDraw.Draw(image)

            words_list = msg_str.split()
            line_max_lenght = 400
            out_str = ''

            loop_str = ''
            for w in words_list:
                try_str = loop_str + ' ' + w
                if img_drawer.textlength( try_str, font=fnt) < line_max_lenght:
                    loop_str = try_str
                else:
                    out_str += loop_str+'\n'
                    loop_str=''
            out_str += loop_str

            img_drawer.multiline_text(canvas_start, out_str, font=fnt,
                                      fill=(255, 255, 255, 255))
            bbox = img_drawer.multiline_textbbox(
                                    canvas_start, out_str, font=fnt)
            bbox_center_x = (bbox[0] + bbox[2])/2
            x0 = int(bbox_center_x - line_max_lenght/2)
            x2 = int(bbox_center_x + line_max_lenght/2)
            bbox = (x0,bbox[1],x2,bbox[3])
            bbox_extend = [bbox[0]-10, bbox[1]-10, bbox[2]+10, bbox[3]+10]
            img_drawer.rounded_rectangle(
                bbox_extend, radius=10, fill=None, outline=(243, 193, 44, 255), width=2)
            bbox_border = [bbox[0]-11, bbox[1]-11, bbox[2]+12, bbox[3]+12]

        elif self.message_type == 'game_hint':
            self.message_pos = (-0.36, -0.33)
            canvas_size = (500, 100)
            canvas_start = (20, 20)
            if not self.message_str:
                msg_str = "That target is invulnerable."
            else:
                msg_str = self.message_str

            image = Image.new("RGBA", canvas_size, (30, 30, 30, 0))
            img_drawer = ImageDraw.Draw(image)

            img_drawer.text(canvas_start, msg_str, font=fnt,
                            fill=(0xff, 0xcc, 0, 255))
            bbox = img_drawer.textbbox(canvas_start, msg_str, font=fnt)
            bbox_border = [bbox[0]-1, bbox[1]-1, bbox[2]+2, bbox[3]+2]

        elif self.message_type == 'chat_hint':
            self.message_pos = (-0.98, -0.26)
            canvas_size = (600, 200)
            canvas_start = (20, 20)
            if not self.message_str:
                msg_str = "[All] Player1: Replace this error message with something meaningful!"
            else:
                msg_str = self.message_str

            image = Image.new("RGBA", canvas_size, (30, 30, 30, 0))
            img_drawer = ImageDraw.Draw(image)

            words_list = msg_str.split()
            line_max_lenght = 500
            out_str = ''

            loop_str = ''
            for w in words_list:
                try_str = loop_str + ' ' + w
                if img_drawer.textlength( try_str, font=fnt) < line_max_lenght:
                    loop_str = try_str
                else:
                    out_str += loop_str+'\n'
            out_str += loop_str

            img_drawer.multiline_text(canvas_start, out_str, font=fnt,
                                      fill=(255, 255, 255, 255))
            bbox = img_drawer.multiline_textbbox(
                canvas_start, out_str, font=fnt)
            bbox_border = [bbox[0]-1, bbox[1]-1, bbox[2]+2, bbox[3]+2]
        else:
            raise LookupError(f'unknown hint type name: {self.message_type}')

        FLIP_TOP_BOTTOM = 1
        img = image.crop(bbox_border).transpose(method=FLIP_TOP_BOTTOM)
        return img

        # img.show()
        # print()
        # image.show()

    def __init__(self, manager: TextBoxManager, msg_type, msg_str='', msg_pos=(0, 0)):
        self.manager = manager
        self.message_type = msg_type
        self.message_str = msg_str
        self.message_pos = msg_pos
        self.message_life_time = 5000

        image = self.generate_texture_image()
        self.text_texture = TextBoxTexture(image)

        scr_w, scr_h = manager.current_screen_size
        img_w, img_h = image.size
        off_x, off_y = self.message_pos
        v_scale = (2*img_w/scr_w, 2*img_h/scr_h, 1, 1)
        v_offset = (off_x, off_y, 0, 0)
        vertices = self.vertices_raw*v_scale+v_offset

        vertices = vertices.astype('f4')

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes,
                     vertices, GL_STATIC_DRAW)
        # position_z
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))
        glBindVertexArray(0)

    def update(self):
        self.message_life_time -= self.manager.frametime
        # print(self.message_life_time )
        if self.message_life_time < 0:
            self.destroy()

    def update_with_screen_resize(self, width, height):
        return
        vertices = []
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes,
                     vertices, GL_STATIC_DRAW)

    def render(self):
        glBindVertexArray(self.vao)
        self.text_texture.use()
        glDrawArrays(GL_TRIANGLES, 0, 6)

    def destroy(self):
        # print('destroy')
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo, ))
        self.text_texture.destroy()
        self.manager.text_box_list.remove(self)


class TextBoxEngine:
    # Auxiliary lines
    def create_shader(self, vertex_filepath, fragment_filepath):

        with open(vertex_filepath, 'r') as f:
            vertex_src = f.readlines()
        with open(fragment_filepath, 'r') as f:
            fragment_src = f.readlines()
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))

        return shader

    def __init__(self):

        self.program = self.create_shader(
            TEXT_HINT_SHADER_FOLDER + "textbox.vert",
            TEXT_HINT_SHADER_FOLDER + "textbox.frag")

        # ########################
        glUseProgram(self.program)

        self.branchIdLoc_1ui = glGetUniformLocation(self.program, "branch_ID")
        self.colorLoc_3f = glGetUniformLocation(self.program, "inColor")
        self.windowSizeLoc_2f = glGetUniformLocation(
            self.program, "window_size")

    def render(self, text_box_list=[]):
        if text_box_list:
            glUseProgram(self.program)
            for k in text_box_list:
                # glUniform3f(self.colorLoc_3f, *k.color)
                # glUniform1ui(self.branchIdLoc_1ui,  1)
                glClear(GL_DEPTH_BUFFER_BIT)
                k.render()

    def destroy(self) -> None:
        glDeleteProgram(self.program)


class TextBoxTexture():

    def __init__(self, image: Image):

        self.unit = 0
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        image_width, image_height = image.size
        # img = image.convert("RGBA")
        img_data = image.tobytes()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width,
                     image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        # glGenerateMipmap(GL_TEXTURE_2D)

    def use(self) -> None:
        # glBindTextureUnit(GL_TEXTURE0 + self.unit, texture)
        glActiveTexture(GL_TEXTURE0)
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
    my_app.add_manager(TextBoxManager(auto_update=True))
    my_app.run()
    my_app.quit()
