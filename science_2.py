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

def newline_join(string, line_length):
    array = string.split()
    count = 0
    line = ""
    for word in array:
        count = count + len(word) + 1
        if count > line_length:
            line = line + "\n" + word
            count = len(word)
        else:
            line = line + " " + word
            
    return(line.strip())

# fonts declaration -----------------------------------------------------------
arial_18 = ImageFont.truetype("arial.ttf", 18)
arial_bold_30 = ImageFont.truetype("arial_bold.ttf", 30)
arial_bold_72 = ImageFont.truetype("arial_bold.ttf", 72)

letters_per_heading = 45

# page URL --------------------------------------------------------------------
url = "http://www.sciencemag.org/news/latest-news"

# parse html ------------------------------------------------------------------
page = requests.get(url)
tree = html.fromstring(page.content)

# parse pictures, headlines and dates -----------------------------------------
picture = tree.xpath('//div[@class="media__icon"]/a/img/@src')

picture_address_sanitized = []
for pic in picture:
    pic = pic.split('?')[0]
    pic = "http:"+pic
    picture_address_sanitized.append(pic)

# download images and resize them for two column HD size picture
images = [ Image.open(requests.get(x, stream=True).raw) for x in picture_address_sanitized ]
images_resized = [ resize_img_to_x(x, 250) for x in images ]

headline = []
for a in tree.xpath('//h2[@class="media__headline"]/a'):
    headline.append(" ".join([ t.strip() for t in a.itertext()]))
headline = [newline_join(x, letters_per_heading) for x in headline ]

author = tree.xpath('//p[@class="byline"]/a/text()')
date = tree.xpath('//p[@class="byline"]/time/text()')

# TODO parse information about journal
#source_1 = tree.xpath('//p[@class="sourceline"]/a/cite/text()')
#source_2 = tree.xpath('//p[@class="sourceline"]/a/text()')
#source_2 = [ x.strip() for x in source_2 ]

# image creation --------------------------------------------------------------
img = Image.new("RGB", (1920, 1080), color = (255,255,255))

# use alpha mode for overlay
draw = ImageDraw.Draw(img, "RGB")

# heading
draw.rectangle([0,0, 1920, 120], fill = (0,0,0))
draw.text((50,15), "AAAS Science - News", fill=(255,255,255), font=arial_bold_72)

# positions and increments to fill a two-column image
x_pos = 0
y_pos = 130
y_displacement = 160
x_displacement = 960
count = 0

# generate output image
for index, image in enumerate(images_resized):
    row_position = index // 6
    column_position = index % 6
    x_coord = x_pos + (x_displacement*row_position)
    y_coord = y_pos + (y_displacement*column_position)
    img.paste(image, (x_coord+10, y_coord))
#    black_rectangle_coord = [x_coord+10, y_coord+10, x_coord+x_displacement-10, y_coord+y_displacement-220]
#    draw.rectangle(black_rectangle_coord, fill = (0,0,0, 160))
    draw.text((x_coord+280,y_coord+5), headline[index], fill=(0,0,0), font=arial_bold_30)
    draw.text((x_coord+280,y_coord+80), author[index], fill=(128,128,128), font=arial_18)
    draw.text((x_coord+280,y_coord+110), date[index], fill=(128,128,128), font=arial_18)

# save image
img.save("/home/igocer/tv/science_news_2.jpg", quality = 100)