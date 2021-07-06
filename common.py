#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw

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

# max line lengths
max_letters = {
    "headline": 45, # breaks at the end of the word that exceeds char number
    "comment": 80 # breaks at the end of the word that exceeds char number
}

# positions and offsets to fill a two-column image
coord = {
    "x": 0,     # x-origin
    "y": 130,   # y-origin, accounts for slide heading
    "xd": 960,  # x-distance of next highlight
    "yd": 160,  # y-distance of next highlight
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

def shorten_authors(auth_string, display_auth = 6):
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

def add_highlights(img, heading, highlights, coord, fonts, num_items = 6):
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
    draw.rectangle([0,0, 1920, 120], fill = (0,0,0))
    draw.text((50,15), heading, fill=(255,255,255), font=fonts['fb72'])
    
    # highlights
    for i, entry in enumerate(highlights[0:(num_items-1)]):
        row = i // num_items
        column = i % num_items
        xpos = coord['x'] + (coord['xd']*row)
        ypos = coord['y'] + (coord['yd']*column)
        img.paste(entry['img'], (xpos+10, ypos))
        draw.text((xpos+coord['px'], ypos+coord['ho']), 
                  entry['headline'],
                  fill=(0,0,0),
                  font=fonts['fb30'])
        draw.text((xpos+coord['px'],ypos+coord['ao']), 
                  entry['authors'], 
                  fill=(128,128,128), 
                  font=fonts['f18'])
        draw.text((xpos+coord['px'],ypos+coord['po']), 
                  entry['publication'], 
                  fill=(128,128,128), 
                  font=fonts['f18'])
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


def process_entry(entry):
    """
    

    Parameters
    ----------
    entry : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    # TODO resize images
    entry['img'] = "https:" + entry['img']
    entry['headline'] = newline_join(entry['headline'], max_letters['headline'])
    entry['authors'] = shorten_authors(entry['authors'])
    entry['comment']: newline_join(entry['comment'], max_letters['comment'])
    return(entry)