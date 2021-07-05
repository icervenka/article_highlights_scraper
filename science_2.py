#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports ---------------------------------------------------------------------
import argparse
from bs4 import BeautifulSoup
import requests
from PIL import Image, ImageDraw, ImageFont
import common

# argparse ---------------------------------------------------------
parser = argparse.ArgumentParser(description='Save image with article highlights from sciencemag.org webpage')
parser.add_argument('--fontdir', type=str, default='.',
                    help='path where fonts are stored (default: current dir)')
parser.add_argument('--font_face', type=str, nargs=2, default='arial arial_bold',
                    help='base name of regular and emphasized font face file ' + 
                    '(default: arial arial_bold)')
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

# max text dimesions ----------------------------------------------------------
letters_per_heading = 45
letters_per_comment = 80

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
url = "http://www.sciencemag.org/news/latest-news"

# parse html ------------------------------------------------------------------
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
highlights = soup.findAll('article')

# parse pictures, headlines and dates -----------------------------------------
h = []
for item in highlights:
    try:
        img = item.find("div", {"class": "media__icon"}).a.img
        headline = item.find("h2", {"class": "media__headline"})
        authors = item.find("p", {"class": "byline"})
        publication = item.find("div", {"class": "media__deck"})
    
        #TODO resize images
        h.append({
            "img": "https:" + img['src'],
            "headline": common.newline_join(headline.get_text().strip(),
                                            letters_per_heading),
            "authors": authors.get_text().strip(),
            "publication": common.newline_join(publication.get_text().strip(),
                                               letters_per_comment)
        })
    # I don't really want the ones that don't have complete info, so I just skip them
    except (TypeError, AttributeError):
        continue

# image creation --------------------------------------------------------------
if args.bg == "none":
    img = Image.new("RGB", (1920, 1080), color = (255,255,255))
else:
    img = Image.open(args.bg)

# use alpha mode for overlay
draw = ImageDraw.Draw(img, "RGB")

# heading
draw.rectangle([0,0, 1920, 120], fill = (0,0,0))
draw.text((50,15), "AAAS Science - News", fill=(255,255,255), font=fb72)


# xd was 280 for this
# TODO ideally move to function
num_items = 6
for i, entry in enumerate(h[0:(num_items-1)]):
    row = i // num_items
    column = i % num_items
    xpos = coord['x'] + (coord['xd']*row)
    ypos = coord['y'] + (coord['yd']*column)
    img.paste(entry['img'], (xpos+10, ypos))
    draw.text((xpos+coord['px'], ypos+coord['ho']), 
              entry['headline'],
              fill=(0,0,0),
              font=fb30)
    draw.text((xpos+coord['px'],ypos+coord['ao']), 
              entry['authors'], 
              fill=(128,128,128), 
              font=f18)
    draw.text((xpos+coord['px'],ypos+coord['po']), 
              entry['publication'], 
              fill=(128,128,128), 
              font=f18)

# save image
img.save(args.outdir + "/" + "science_news.jpg", quality = 100)