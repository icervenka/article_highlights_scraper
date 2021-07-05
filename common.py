#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw

"""

"""
# various constants -----------------------------------------------------------
# max line lengths
max_letters = {
    "heading": 45,
    "comment": 80
}

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
