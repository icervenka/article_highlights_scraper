#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 17:37:57 2021

@author: igocer
"""

from PIL import Image

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



