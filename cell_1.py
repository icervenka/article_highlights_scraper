#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports ---------------------------------------------------------------------
import argparse
# TODO switch to beautifulSoup
from bs4 import BeautifulSoup
from lxml import html
import requests
from PIL import Image, ImageDraw, ImageFont
import common

def shorten_authors(auth_string, display_auth = 6):
    s = auth_string.split(',')
    s = [x.strip() for x in s]
    if len(s) >= (display_auth+1):
        s = s[0:(display_auth-1)] + ["..."] + s[-1]
    return ", ".join(s)


# argparse ---------------------------------------------------------
parser = argparse.ArgumentParser(description='Save image with article highlights from cell.com webpage')
parser.add_argument('--fontdir', type=str, default='.',
                    help='path where fonts are stored (default: current dir)')
parser.add_argument('--font_face', type=str, nargs=2, default='arial arial_bold',
                    help='base name of regular and emphasized font face file (default: arial arial_bold)')
# TODO maybe do default white full HD image
parser.add_argument('--bg', type=str, default='none',
                    help='path to HD background image to draw the highlights on.' +
                    'Defaults to white background. (default: none)')
parser.add_argument('-o', '--outdir', type=str, default='.',
                    help='path where to store output (default: current dir)')
args = parser.parse_args()

# fonts declaration -----------------------------------------------------------
font_dir = args.fontdir
f18 = ImageFont.truetype(font_dir + "/" + args.font_face[0] + ".ttf", 18)
fb30 = ImageFont.truetype(font_dir + "/" + args.font_face[1] + ".ttf", 30)
fb72 = ImageFont.truetype(font_dir + "/" + args.font_face[1] + ".ttf", 72)

letters_per_heading = 45

# positions and offsets to fill a two-column image
coord = {
    "x": 0,
    "y": 130,
    "xd": 960,
    "yd": 160,
    "px": 230,
    "ho": 5,
    "ao": 80,
    "po": 110
}

# page URL --------------------------------------------------------------------
url = "https://www.cell.com/cell/current"

# parse html ------------------------------------------------------------------
page = requests.get(url)
tree = html.fromstring(page.content)

# parse pictures, headlines and dates -----------------------------------------
picture = tree.xpath('//div[@class="cellp_postImg"]/img/@src')
picture_prepend_string = "http://www.cell.com:80"

picture_address_sanitized = []
for pic in picture:
    if not pic.startswith("http"):
        pic = picture_prepend_string + pic
    picture_address_sanitized.append(pic)    

# download images and resize them for two column HD size picture
images = [ Image.open(requests.get(x, stream=True).raw) for x in picture_address_sanitized ]
images_resized = [ common.resize_img_to_x(x, 190) for x in images ]

headline = tree.xpath('//div[@class="cellp_postTitle"]/a/text()')
headline = [ x.strip() for x in headline ]
headline = [common.newline_join(x, letters_per_heading) for x in headline ]

author = tree.xpath('//div[@class="cellp_postAuthors"][1]/text()')
author = [ x.strip() for x in author ]

publication = tree.xpath('//div[@class="cellp_postPub"]/a/text()')
publication = [ x.strip() for x in publication ]

# image creation --------------------------------------------------------------
# standard full HD size
# TODO add more sizes
if args.bg == "none":
    img = Image.new("RGB", (1920, 1080), color = (255,255,255))
else:
    img = Image.open(args.bg)

# use alpha mode for overlay
draw = ImageDraw.Draw(img, "RGB")

# heading
draw.rectangle([0,0, 1920, 120], fill = (0,0,0))
draw.text((50,15), "Cell - News", fill=(255,255,255), font=fb72)

# TODO ideally move to function
num_items = 6
for i, image in enumerate(images_resized):
    row = i // num_items
    column = i % num_items
    xpos = coord['x'] + (coord['xd']*row)
    ypos = coord['y'] + (coord['yd']*column)
    img.paste(image, (xpos+10, ypos))
    draw.text((xpos+coord['px'], ypos+coord['ho']), 
              headline[i],
              fill=(0,0,0),
              font=fb30)
    draw.text((xpos+coord['px'],ypos+coord['ao']), 
              author[i], 
              fill=(128,128,128), 
              font=f18)
    draw.text((xpos+coord['px'],ypos+coord['po']), 
              publication[i], 
              fill=(128,128,128), 
              font=f18)

# save image
img.save(args.outdir + "cell_news.jpg", quality = 100)