#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

"""

# imports ---------------------------------------------------------------------
import argparse
from bs4 import BeautifulSoup
import requests
from PIL import Image, ImageFont
import common as c

# argparse --------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Save image with article ' + 
                                 'highlights from journal webpage')
parser.add_argument('--journal', type=str, default='cell', 
                    choices=['cell', 'science', 'nature'],
                    help='journal to get highlights from (default: cell)')
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

# font declaration ------------------------------------------------------------
fonts = {
    "f18": ImageFont.truetype(args.fontdir + "/" + args.font_face[0] + ".ttf", 18),
    "fb30": ImageFont.truetype(args.fontdir + "/" + args.font_face[1] + ".ttf", 30),
    "fb72": ImageFont.truetype(args.fontdir + "/" + args.font_face[1] + ".ttf", 72)
}

# parse html ------------------------------------------------------------------
response = requests.get(c.journals[args.journal]['url'])
soup = BeautifulSoup(response.text, "html.parser")

# image creation --------------------------------------------------------------
# standard full HD size
# TODO add more sizes
# TODO bg doesn't work yet, function draws black rectangle as headline bg
if args.bg == "none":
    img = Image.new("RGB", (1920, 1080), color = (255,255,255))
else:
    img = Image.open(args.bg)

# parse and process highlights from page tree
highlights = [ c.process_entry(x) for x in c.extract_entries(soup, args.journal) ]

# draw highlights on top of image
img = c.add_highlights(img, 
                       c.journals[args.journal]['headline'], 
                       highlights, 
                       c.coord, 
                       fonts)

# save image
img.save(args.outdir + c.journals[args.journal]['filename'], quality = 100)