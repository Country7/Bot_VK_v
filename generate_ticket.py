# -*- coding: utf-8 -*-
from io import BytesIO
from random import randint

import requests
from PIL import Image, ImageDraw, ImageFont


TEMPLATE_PATH = "files/ticket_base.png"
FONT_PATH = "files/Roboto-Bold.ttf"
AVATAR_PATH = "files/avatars/avatar_"
FONT_SIZE = 32
FONT_COLOR = (255, 255, 255, 255)
NAME_OFFSET = (316, 306)
EMAIL_OFFSET = (316, 358)
AVATAR_WIDTH = '116'
AVATAR_HEIGHTS = '141'
AVATAR_OFFSET = (39, 226)


def dice():
    return str(randint(0, 9))


def generate_ticket(name, email):
    # get an image
    with Image.open(TEMPLATE_PATH).convert("RGBA") as image_base:
        # get a font
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        # get a drawing context
        image_draw = ImageDraw.Draw(image_base)
        # draw text, full opacity
        image_draw.text(NAME_OFFSET, name, font=font, fill=FONT_COLOR, anchor='mb')
        image_draw.text(EMAIL_OFFSET, email, font=font, fill=FONT_COLOR, anchor='mb')

        avatar_file_name = f'{AVATAR_PATH}{dice()}.png'
        with Image.open(avatar_file_name) as avatar:
            image_base.paste(avatar, box=AVATAR_OFFSET)

        # with open("files/ticket_examp.png", 'wb') as file_ticket_example:
        #     image_base.save(file_ticket_example, 'png')
        # image_base.show()
        temp_file = BytesIO()
        image_base.save(temp_file, 'png')
        temp_file.seek(0)

        return temp_file

