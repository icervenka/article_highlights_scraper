#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports ---------------------------------------------------------------------
import argparse
from lxml import html
import requests
from PIL import Image, ImageDraw, ImageFont
import common

# argparse ---------------------------------------------------------
parser = argparse.ArgumentParser(description='Save image with article highlights from sciencemag.org webpage')
parser.add_argument('--fontdir', type=str, default='.',
                    help='path where fonts are stored (default: current dir)')
parser.add_argument('--font_face', type=str, nargs=2, default='arial arial_bold',
                    help='base name of regular and emphasized font face file (default: arial arial_bold)')
parser.add_argument('-o', '--outdir', type=str, default='.',
                    help='path where to store output (default: current dir)')
args = parser.parse_args()

# fonts declaration -----------------------------------------------------------
font_dir = args.fontdir
f18 = ImageFont.truetype(font_dir + "/" + args.font_face[0] + ".ttf", 18)
fb30 = ImageFont.truetype(font_dir + "/" + args.font_face[1] + ".ttf", 30)
fb72 = ImageFont.truetype(font_dir + "/" + args.font_face[1] + ".ttf", 72)

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
images_resized = [ common.resize_img_to_x(x, 250) for x in images ]

headline = []
for a in tree.xpath('//h2[@class="media__headline"]/a'):
    headline.append(" ".join([ t.strip() for t in a.itertext()]))
headline = [ common.newline_join(x, letters_per_heading) for x in headline ]

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
draw.text((50,15), "AAAS Science - News", fill=(255,255,255), font=fb72)

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
    draw.text((x_coord+280,y_coord+5), headline[index], fill=(0,0,0), font=fb30)
    draw.text((x_coord+280,y_coord+80), author[index], fill=(128,128,128), font=f18)
    draw.text((x_coord+280,y_coord+110), date[index], fill=(128,128,128), font=f18)

# save image
img.save(args.outdir + "/" + "science_news.jpg", quality = 100)