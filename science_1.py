#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports ---------------------------------------------------------------------
from lxml import html
import requests
from PIL import Image, ImageDraw, ImageFont

# function definition ---------------------------------------------------------

# resize image to specific width maintaining aspect ratio
def resize_img_to_x(image, x):
    return(image.resize((x, int(x/(image.size[0]/image.size[1]))), Image.ANTIALIAS))

# fonts declaration -----------------------------------------------------------
arial_24 = ImageFont.truetype("arial.ttf", 24)
arial_bold_32 = ImageFont.truetype("arial_bold.ttf", 32)
arial_bold_72 = ImageFont.truetype("arial_bold.ttf", 72)

# page URL --------------------------------------------------------------------
url = "http://www.sciencemag.org/"

# parse html ------------------------------------------------------------------
page = requests.get(url)
tree = html.fromstring(page.content)

# parse pictures, headlines and dates -----------------------------------------
picture = tree.xpath('//div[@class="hero__image"]/a/img/@src')

picture_address_sanitized = []
for pic in picture:
    pic = pic.split('?')[0]
    pic = "http:"+pic
    picture_address_sanitized.append(pic)

# download images and resize them for two column HD size picture
images = [ Image.open(requests.get(x, stream=True).raw) for x in picture_address_sanitized ]
images_resized = [ resize_img_to_x(x, 960) for x in images ]

headline = list(tree.xpath('//h2[@class="hero__headline"]/a/text()'))
headline = [ str(x).strip() for x in headline ]

date = tree.xpath('//p[@class="sourceline"]/a/time/span/text()')

# TODO parse information about journal
#source_1 = tree.xpath('//p[@class="sourceline"]/a/cite/text()')
#source_2 = tree.xpath('//p[@class="sourceline"]/a/text()')
#source_2 = [ x.strip() for x in source_2 ]

# image creation --------------------------------------------------------------
img = Image.new("RGB", (1920, 1080), color = (255,255,255))

# use alpha mode for overlay
draw = ImageDraw.Draw(img, "RGBA")

# heading
draw.rectangle([0,0, 1920, 120], fill = (0,0,0))
draw.text((50,15), "AAAS Science - News", fill=(255,255,255), font=arial_bold_72)

# positions and increments to fill a two-column image
x_pos = 0
y_pos = 120
y_displacement = 320
x_displacement = 960
count = 0

# generate output image
for index, image in enumerate(images_resized):
    row_position = index // 3
    column_position = index % 3
    x_coord = x_pos + (x_displacement*row_position)
    y_coord = y_pos + (y_displacement*column_position)
    img.paste(image, (x_coord, y_coord))
    black_rectangle_coord = [x_coord+10, y_coord+10, x_coord+x_displacement-10, y_coord+y_displacement-220]
    draw.rectangle(black_rectangle_coord, fill = (0,0,0, 160))
    draw.text((x_coord+20,y_coord+20), headline[index], color=(255,255,255,255), font=arial_bold_32)
    draw.text((x_coord+20,y_coord+65), date[index], color=(255,255,255,255), font=arial_24)

# save image
img.save("/home/igocer/tv/science_news_1.jpg", quality = 100)