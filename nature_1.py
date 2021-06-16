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
arial_24 = ImageFont.truetype("arial.ttf", 24)
arial_18 = ImageFont.truetype("arial.ttf", 18)
arial_bold_24 = ImageFont.truetype("arial_bold.ttf", 24)
arial_bold_72 = ImageFont.truetype("arial_bold.ttf", 72)

letters_per_heading = 55
letters_per_comment = 80

# page URL --------------------------------------------------------------------
url = "http://www.nature.com/news/index.html"

# parse html ------------------------------------------------------------------
page = requests.get(url)
tree = html.fromstring(page.content)

# parse pictures, headlines and dates -----------------------------------------
url_level2 = tree.xpath('//div[@class="col left"]/descendant::*/h3/a/@href')
picture_1 = []
for u in url_level2:   
    page = requests.get(u)
    tree2 = html.fromstring(page.content)
    picture_1.append(tree2.xpath('//div[@class="img img-middle"][1]/descendant::*/img/@src'))

picture_2 = []
for u in url_level2:   
    page = requests.get(u)
    tree2 = html.fromstring(page.content)
    picture_2.append(tree2.xpath('//img[@class="figure__image"]/@src'))

picture = []
for f, s in zip(picture_1, picture_2):
    if not f:
        picture.append("http:"+s[0])
    else:
        picture.append("http://www.nature.com"+f[0])


# download images and resize them for two column HD size picture
images = [ Image.open(requests.get(x, stream=True).raw) for x in picture]
images_resized = [ resize_img_to_x(x, 190) for x in images ]

headline = tree.xpath('//div[@class="col left"]/descendant::*/h3/a/text()')

headline = []
for a in tree.xpath('//div[@class="col left"]/descendant::*/h3/a'):
    headline.append(" ".join([ t.strip() for t in a.itertext()]))
headline = [ x.strip() for x in headline ]
headline = [newline_join(x, letters_per_heading) for x in headline ]

comment = tree.xpath('//div[@class="col left"]/descendant::*/p[@class="standfirst truncate to-200"]/text()')
comment = [ x.strip() for x in comment ]
comment = [newline_join(x, letters_per_comment) for x in comment ]


# image creation --------------------------------------------------------------
img = Image.new("RGB", (1920, 1080), color = (255,255,255))

# use alpha mode for overlay
draw = ImageDraw.Draw(img, "RGB")

# heading
draw.rectangle([0,0, 1920, 120], fill = (0,0,0))
draw.text((50,15), "Nature - News", fill=(255,255,255), font=arial_bold_72)

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
    draw.text((x_coord+230,y_coord), headline[index], fill=(0,0,0), font=arial_bold_24)
    draw.text((x_coord+230,y_coord+65), comment[index], fill=(128,128,128), font=arial_18)

# save image
img.save("/home/igocer/tv/nature_news_1.jpg", quality = 100)