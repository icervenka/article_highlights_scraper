#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw
import requests

"""

"""

# various constants -----------------------------------------------------------
# urls and other journal specific values
journals = {
    "cell": {
        "url": "https://www.cell.com/cell/current",
        "headline": "Cell - News",
        "filename": "cell_news.jpg",
        },
    "science": {
        "url": "http://www.sciencemag.org/news/latest-news",
        "headline": "Science - News",
        "filename": "science_news.jpg",
        },
    "nature": {
        "url": "https://www.nature.com/nature/research-articles",
        "headline": "Nature - News",
        "filename": "nature_news.jpg",
        }
    }

# image width for graphical abstract in pixels
highlight_img_width = 190

# max line lengths
max_letters = {
    "headline": 60, # breaks at the end of the word that exceeds char number
    "comment": 100 # breaks at the end of the word that exceeds char number
}

# positions and offsets to fill a two-column image
coord = {
    "x": 0,     # x-origin
    "y": 110,   # y-origin, accounts for slide heading
    "xd": 960,  # x-distance of next highlight
    "yd": 230,  # y-distance of next highlight
    "px": 230,  # x-padding to the right of image
    "ho": 5,    # y-offset for individual article heading
    "ao": 80,   # y-offset for individual author list 
    "po": 110   # y-offset for individual comment
}

# function definition ---------------------------------------------------------

# resize image to specific width maintaining aspect ratio
def resize_img_to_x(image, x):
    """
    

    Parameters
    ----------
    image : TYPE
        DESCRIPTION.
    x : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    return(image.resize((x, int(x/(image.size[0]/image.size[1]))), Image.ANTIALIAS))

def newline_join(string, line_length):
    """
    

    Parameters
    ----------
    string : TYPE
        DESCRIPTION.
    line_length : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
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

def shorten_authors(auth_string, display_auth = 5):
    """
    

    Parameters
    ----------
    auth_string : TYPE
        DESCRIPTION.
    display_auth : TYPE, optional
        DESCRIPTION. The default is 6.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    s = auth_string.split(',')
    s = [x.strip() for x in s]
    if len(s) >= (display_auth+1):
        s = s[0:(display_auth-1)] + ["..."] + [s[-1]]
    return ", ".join(s)

def add_highlights(img, heading, highlights, coord, fonts, items = 8, columns = 2):
    """
    

    Parameters
    ----------
    img : TYPE
        DESCRIPTION.
    heading : TYPE
        DESCRIPTION.
    highlights : TYPE
        DESCRIPTION.
    coord : TYPE
        DESCRIPTION.
    fonts : TYPE
        DESCRIPTION.
    num_items : TYPE, optional
        DESCRIPTION. The default is 6.

    Returns
    -------
    draw : TYPE
        DESCRIPTION.

    """
    # use alpha mode for overlay
    draw = ImageDraw.Draw(img, "RGB")
    
    # heading
    draw.rectangle([0,0, 1920, 90], fill = (0,0,0))
    draw.text((50,15), heading, fill=(255,255,255), font=fonts['main'])
    
    # highlights
    for i, entry in enumerate(highlights[0:items]):
        row = i // (items//columns)
        col = i % (items//columns)
        xpos = coord['x'] + (coord['xd']*row)
        ypos = coord['y'] + (coord['yd']*col)
        img.paste(entry['img'], (xpos+10, ypos))
        draw.text((xpos+coord['px'], ypos+coord['ho']), 
                  entry['headline'],
                  fill=(0,0,0),
                  font=fonts['heading'])
        draw.text((xpos+coord['px'],ypos+coord['ao']), 
                  entry['authors'], 
                  fill=(102,102,102), 
                  font=fonts['text'])
        draw.text((xpos+coord['px'],ypos+coord['po']), 
                  entry['comment'], 
                  fill=(102,102,102),
                  font=fonts['text'])
    return draw

# TODO this is a messy function with a lot of repeated code, try to break it 
# apart, isolating the most common parts
def extract_entries(soup, journal):
    """
    

    Parameters
    ----------
    soup : TYPE
        DESCRIPTION.
    journal : TYPE
        DESCRIPTION.

    Returns
    -------
    entries : TYPE
        DESCRIPTION.

    """
    entries = []

    if(journal == "cell"):
        articles = soup.find(id = "Articles").parent.findAll("div", {"class": "articleCitation"})
        for item in articles:
            try:
                entries.append({
                    "img": item.find("div", {"class": "toc__item__cover"}).a.img['src'],
                    "headline": item.find("h3", {"class": "toc__item__title"}).get_text().strip(),    
                    "authors": item.find("ul", {"class": "toc__item__authors"}).get_text().strip(),
                    "comment": item.find("div", {"class": "toc__item__details"}).get_text().strip()
                })
            # I don't really want the ones that don't have complete info, so I just skip them
            except (TypeError, AttributeError):
                continue
    if(journal == "science"):
        articles = soup.find(id = "Articles").parent.findAll("div", {"class": "articleCitation"})
        for item in articles:
            try:
                entries.append({
                    "img": item.find("div", {"class": "media__icon"}).a.img['src'],
                    "headline": item.find("h2", {"class": "media__headline"}).get_text().strip(),    
                    "authors": item.find("p", {"class": "byline"}).get_text().strip(),
                    "comment": item.find("div", {"class": "media__deck"}).get_text().strip()
                })
            # I don't really want the ones that don't have complete info, so I just skip them
            except (TypeError, AttributeError):
                continue
    if(journal == "nature"):
        articles = soup.find(id = "Articles").parent.findAll("div", {"class": "articleCitation"})
        for item in articles:
            try:
                entries.append({
                    "img": item.find("div", {"class": "c-card__image"}).picture.img['src'],
                    "headline": item.find("h3", {"class": "c-card__title"}).get_text().strip(),    
                    "authors": item.find("ul", {"class": "c-author-list"}).get_text().strip(),
                    "comment": item.find("div", {"class": "c-card__summary"}).get_text().strip()
                })
            # I don't really want the ones that don't have complete info, so I just skip them
            except (TypeError, AttributeError):
                continue
            
    return entries


def process_entry(entry, img_width):
    """
    

    Parameters
    ----------
    entry : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    # TODO width of images as parameter
    if not entry['img'].startswith("https"):
        entry['img'] = "https:" + entry['img']
    entry['img'] = resize_img_to_x(Image.open(requests.get(entry['img'], stream=True).raw), img_width)
    entry['headline'] = newline_join(entry['headline'], max_letters['headline'])
    entry['authors'] = shorten_authors(entry['authors'])
    entry['comment'] = newline_join(entry['comment'], max_letters['comment'])
    return(entry)