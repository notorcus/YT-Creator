import os
import csv
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File {file_path} has been deleted.")
    except OSError as e:
        print(f"Error: {file_path} : {e.strerror}")

def convert_to_seconds(timestamp, timebase):
    hh, mm, ss, ff = map(int, timestamp.split(':'))
    return hh * 3600 + mm * 60 + ss + ff * timebase

def seconds_to_time(seconds):
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d:%02d" % (hours, minutes, seconds)

def convert_srt_to_secs(timestamp):
    hh, mm, ss = map(float, timestamp.split(':'))
    return hh * 3600 + mm * 60 + ss

def parse_srt(srt_file):
    with open(srt_file, 'r') as file:
        lines = file.readlines()

    captions = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()  # strip the line
        if line.isdigit():  # skip index line
            i += 1
            line = lines[i].strip()  # strip the next line

        if line:  # if the line is not empty
            # split timestamp line into start and end times
            start_time, end_time = map(str.strip, line.split('-->'))
            i += 1

            # read all subsequent lines until an empty line (the text of the subtitle)
            text_lines = []
            while i < len(lines) and lines[i].strip():  # check if the stripped line is not empty
                text_lines.append(lines[i].strip())
                i += 1
            text = ' '.join(text_lines)

            captions.append((start_time, end_time, text))
        i += 1  # skip empty line or move to the next line

    return pd.DataFrame(captions, columns=['start', 'end', 'caption'])

def make_text_image(caption):
    font_path = r'c:\\Users\\Akshat Kumar\\Editing\\packs\\ORCUS pack\\Fonts\\Noir Pro\\NoirPro-SemiBold.otf'
    font_size = 50
    font = ImageFont.truetype(font_path, font_size)
    text_color = (255, 255, 255, 255)  # white color with full opacity
    stroke_color = (0, 0, 0, 255)  # black color for stroke
    shadow_color = (0, 0, 0, 128)  # half-transparent black color for shadow
    stroke_width = 3
    shadow_width = 5
    
    # Calculate the size of the text in pixels
    text_width, text_height = font.getsize(caption)
    
    # Create a transparent image
    image_width, image_height = 640, 480
    image = Image.new('RGBA', (image_width, image_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Calculate the position of the text to be centered
    text_position = ((image_width - text_width) // 2, (image_height - text_height) // 2)

    # Draw stroke
    for dx, dy in [(dx, dy) for dx in range(-stroke_width, stroke_width+1) for dy in range(-stroke_width, stroke_width+1)]:
        draw.text((text_position[0]+dx, text_position[1]+dy), caption, stroke_color, font=font)
    
    # Draw text
    draw.text(text_position, caption, text_color, font=font)

    return np.array(image)

def load_csv(filename):
    with open(filename, 'r') as f:
        return list(csv.DictReader(f))
