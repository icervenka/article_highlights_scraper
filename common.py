#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw
import requests

# various constants -----------------------------------------------------------
# urls and other journal specific values
journals = {
    "cell": {
        "url": "https://www.cell.com/cell/current",
        "heading": "Cell - News",
        "filename": "cell_news.jpg",
        },
    "science": {
        "url": "http://www.sciencemag.org/news/latest-news",
        "heading": "Science - News",
        "filename": "science_news.jpg",
        },
    "nature": {
        "url": "https://www.nature.com/nature/research-articles",
        "heading": "Nature - News",
        "filename": "nature_news.jpg",
        }
    }

# image width for graphical abstract in pixels
highlight_img_width = 190

# colors used in the document
color_white = (255,255,255)
color_black = (0,0,0)
color_grey30 = (102,102,102)

# max line lengths
max_letters = {
    "title": 60, # breaks at the end of the word that exceeds char number
    "comment": 100 # breaks at the end of the word that exceeds char number
}

# positions and offsets to fill a two-column image
coord = {
    "x": 0,     # x-origin
    "y": 110,   # y-origin, accounts for slide heading
    "xd": 960,  # x-distance of next highlight
    "yd": 230,  # y-distance of next highlight
    "px": 230,  # x-padding to the right of image
    "ho": 5,    # y-offset for individual article title
    "ao": 80,   # y-offset for individual author list 
    "po": 110   # y-offset for individual comment
}

# function definition ---------------------------------------------------------

# resize image to specific width maintaining aspect ratio
def resize_img_to_x(image, x):
    """
    Proportionally resizes ImageDraw Image to a specified width

    Parameters
    ----------
    image : ImageDraw Image
        Image to resize.
    x : int
        New width of image in pixels.

    Returns
    -------
    Resized ImageDraw Image scaled proportionally to width 'x'.

    """
    return(image.resize((x, int(x/(image.size[0]/image.size[1]))), Image.ANTIALIAS))

def newline_join(string, line_length):
    """
    Inserts newline into the string. Newline is inserted at first the word 
    boundary after the line_length characters.

    Parameters
    ----------
    string : str
        String to insert newlines into.
    line_length : int
        Line length threshold after which the new line will be inserted.

    Returns
    -------
    str with inserted newlines

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

# TODO science and nature authors not parsed correctly
def shorten_authors(auth_string, display_auth = 5):
    """
    Shortens article author list. By convention first display_auth-1 authors and 
    the last author are shown. The rest is replaced by '...'.

    Parameters
    ----------
    auth_string : str
        Article authors separated by comma.
    display_auth : int, optional
        Maximum number of autors to display. The default is 5.

    Returns
    -------
    str
        Authors with middle ones substituted by '...'.

    """
    s = auth_string.split(',')
    s = [x.strip() for x in s]
    if len(s) >= (display_auth+1):
        s = s[0:(display_auth-1)] + ["..."] + [s[-1]]
    return ", ".join(s)

def add_highlights(img, highlights, heading, coord, fonts, items = 8):
    """
    Draws n highlights on the image specified by items. Draws 90px rectangle
    at the top of the image together with white 'heading' text. Uses 2 column
    layout to distribute the highlights based on offsets specified in 'coord'.
    
    Parameters
    ----------
    img : ImageDraw image
        Image to draw the highlights on.
    highlights : dict
        Highlight dictionary containg following keys: img, title, authors, comment
        see extract_highlights and process_highlights for more info.
    heading : str
        Main image heading.
    coord : dict
        Coordinates and offsets used to draw highlights onto the image.
    fonts : dict of ImageFont
        Dictionary of fonts containg following keys: main, title, text
    items : int, optional
        Number of highlights to draw on the image. The default is 8.

    Returns
    -------
    None

    """
    # use alpha mode for overlay
    draw = ImageDraw.Draw(img, "RGB")
    
    # heading
    draw.rectangle([0,0, 1920, 90], fill=color_black) # black background
    draw.text((50,15), heading, fill=color_white, font=fonts['main']) # white text
    
    # highlights
    for i, entry in enumerate(highlights[0:items]):
        # calculation of highlight coordinates
        row = i // (items//2) # 2-column layout
        col = i % (items//2) # 2-column layout
        xpos = coord['x'] + (coord['xd']*row)
        ypos = coord['y'] + (coord['yd']*col)
        
        # draw image
        img.paste(entry['img'], (xpos+10, ypos))
        # draw accompanying text
        draw.text((xpos+coord['px'], ypos+coord['ho']), 
                  entry['title'],
                  fill=color_black,
                  font=fonts['title'])
        draw.text((xpos+coord['px'],ypos+coord['ao']), 
                  entry['authors'], 
                  fill=color_grey30, 
                  font=fonts['text'])
        draw.text((xpos+coord['px'],ypos+coord['po']), 
                  entry['comment'], 
                  fill=color_grey30,
                  font=fonts['text'])
    return None

# TODO this is a messy function with a lot of repeated code, try to break it 
# apart, isolating the most common parts
def extract_highlights(soup, journal):
    """
    Function that extracts relevant highlight information from DOM tree based on
    the journal specified. Highlight entries that don't have all parameters 
    specified (image, title, authors, comment) are skipped.

    Parameters
    ----------
    soup : bs4.BeautifulSoup
        Html tree of a journal website where articles can be found.
    journal : str
        Journal the html tree was extracted from, one of 'cell', 'science', 'nature'.

    Returns
    -------
    entries : dict of str
        Parsed article highlights containg following keys:
            img: url of an image
            title: article title
            authors: article authors
            comment: commentary about the article
            
    """
    entries = []

    if(journal == "cell"):
        articles = soup.find(id = "Articles").parent.findAll("div", {"class": "articleCitation"})
        for item in articles:
            try:
                entries.append({
                    "img": item.find("div", {"class": "toc__item__cover"}).a.img['src'],
                    "title": item.find("h3", {"class": "toc__item__title"}).get_text().strip(),    
                    "authors": item.find("ul", {"class": "toc__item__authors"}).get_text().strip(),
                    "comment": item.find("div", {"class": "toc__item__details"}).get_text().strip()
                })
            # I don't really want the ones that don't have complete info, so I just skip them
            except (TypeError, AttributeError):
                continue
    if(journal == "science"):
        articles = soup.findAll('article')
        for item in articles:
            try:
                entries.append({
                    "img": item.find("div", {"class": "media__icon"}).a.img['src'],
                    "title": item.find("h2", {"class": "media__headline"}).get_text().strip(),    
                    "authors": item.find("p", {"class": "byline"}).get_text().strip(),
                    "comment": item.find("div", {"class": "media__deck"}).get_text().strip()
                })
            # I don't really want the ones that don't have complete info, so I just skip them
            except (TypeError, AttributeError):
                continue
    if(journal == "nature"):
        articles = soup.findAll('article')
        for item in articles:
            try:
                entries.append({
                    "img": item.find("div", {"class": "c-card__image"}).picture.img['src'],
                    "title": item.find("h3", {"class": "c-card__title"}).get_text().strip(),    
                    "authors": item.find("ul", {"class": "c-author-list"}).get_text().strip(),
                    "comment": item.find("div", {"class": "c-card__summary"}).get_text().strip()
                })
            # I don't really want the ones that don't have complete info, so I just skip them
            except (TypeError, AttributeError):
                continue
            
    return entries


def process_highlight(entry, img_width):
    """
    Function processing highlights extracted from DOM tree. Downloads image based
    on its url and scales it. Prettifies text by inserting newlines and 
    shortening author lists.

    Parameters
    ----------
    entry : dict of str
        Dictionary created by extract_highlights function.
    img_width : int
        Width of image to resize to.

    Returns
    -------
    dict
        Highlight dict with downloaded and resized image and prettified text
        
    """
    # 'https:' is missing in page src links
    if not entry['img'].startswith("https"):
        entry['img'] = "https:" + entry['img']
    # fetch the image and resize it to common width
    entry['img'] = resize_img_to_x(Image.open(requests.get(entry['img'], stream=True).raw), img_width)
    entry['title'] = newline_join(entry['title'], max_letters['title'])
    entry['authors'] = shorten_authors(entry['authors'])
    entry['comment'] = newline_join(entry['comment'], max_letters['comment'])
    return(entry)