#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports ---------------------------------------------------------------------
import argparse
from bs4 import BeautifulSoup
import requests
from PIL import Image, ImageFont
import common as c

# argparse --------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Save image with article ' + 
                                 'highlights from cell.com webpage')
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

# page URL --------------------------------------------------------------------
url = "https://www.cell.com/cell/current"

# parse html ------------------------------------------------------------------
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
soup = soup.find(id = "Articles").parent
articles = soup.findAll("div", {"class": "articleCitation"})

# parse pictures, headlines and dates -----------------------------------------
highlights = []
for item in articles:
    try:
        img = item.find("div", {"class": "toc__item__cover"}).a.img
        headline = item.find("h3", {"class": "toc__item__title"})
        authors = item.find("ul", {"class": "toc__item__authors"})
        publication = item.find("div", {"class": "toc__item__details"})
         
        # TODO resize images
        highlights.append({
            "img": "https:" + img['src'],
            "headline": c.newline_join(headline.get_text().strip(),
                                            c.max_letters['heading']),
            "authors": c.shorten_authors(authors.get_text().strip()),
            "publication": c.newline_join(publication.get_text().strip(),
                                               c.max_letters['comment'])
        })
    # I don't really want the ones that don't have complete info, so I just skip them
    except (TypeError, AttributeError):
        continue

# image creation --------------------------------------------------------------
# standard full HD size
# TODO add more sizes
if args.bg == "none":
    img = Image.new("RGB", (1920, 1080), color = (255,255,255))
else:
    img = Image.open(args.bg)

img = c.add_highlights(img, "Cell - News", highlights, c.coord, fonts)

# save image
img.save(args.outdir + "cell_news.jpg", quality = 100)