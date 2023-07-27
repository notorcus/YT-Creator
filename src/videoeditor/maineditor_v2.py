import csv, os
import numpy as np
import pandas as pd
import glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, ImageClip
from moviepy.config import change_settings
# from videoeditor.silencedetect import silence_detect
from silencedetect import silence_detect
change_settings({"IMAGEMAGICK_BINARY": r"c:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

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

    """
    # Draw shadow
    shadow_image = Image.new('RGBA', (image_width, image_height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_image)
    shadow_draw.text((text_position[0]+shadow_width, text_position[1]+shadow_width), caption, shadow_color, font=font)
    blurred_shadow = shadow_image.filter(ImageFilter.GaussianBlur(radius=5))
    image = Image.alpha_composite(image, blurred_shadow)
    """
    return np.array(image)

def load_csv(filename):
    with open(filename, 'r') as f:
        return list(csv.DictReader(f))

def editvideo(video_path, cutstamp_path, srt_path, num_videos: int):
# Load the video file once
    source_video = VideoFileClip(video_path)

    # Calculate the timebase
    timebase = 1 / source_video.fps

    # Load the caption file
    caption_df = parse_srt(srt_path)

    offset = 0  # Offset in seconds

    # Convert the 'start' and 'end' columns to seconds and offset them
    caption_starts = [convert_srt_to_secs(t) - offset for t in caption_df['start']] 
    caption_ends = [convert_srt_to_secs(t) - offset for t in caption_df['end']] 
    captions = caption_df['caption'].tolist()

    # Get a list of all CSV files
    csv_files = glob.glob(f'{cutstamp_path}/short_*.csv')[:num_videos]

    # Loop over all CSV files
    for i, csv_file in enumerate(csv_files, 1):
        # Read the CSV file
        df = pd.read_csv(csv_file)

        starts = df.iloc[:, 0]  # First column
        ends = df.iloc[:, 1]  # Second column

        clips = []

        # Loop over all rows in the CSV file
        for start, end in zip(starts, ends):
            # Convert timestamps to seconds, create a subclip and add it to the list
            start_sec = convert_to_seconds(start, timebase)
            end_sec = convert_to_seconds(end, timebase)
            clip = source_video.subclip(seconds_to_time(start_sec), seconds_to_time(end_sec))

            # Find all captions that fall within the clip
            clip_captions = [(c_start, c_end, caption) for c_start, c_end, caption in zip(caption_starts, caption_ends, captions) if c_start >= start_sec and c_end <= end_sec]

            # Create an image and a text clip for each caption and add it to a list
            txt_clips = [ImageClip(make_text_image(caption), duration=c_end-c_start).set_start(c_start - start_sec).set_pos('bottom') for c_start, c_end, caption in clip_captions]

            # Add the original clip to the list of text clips
            txt_clips.insert(0, clip)

            # Combine the clip with all text clips
            clip = CompositeVideoClip(txt_clips)

            clips.append(clip)


        # Concatenate all clips together
        final_clip = concatenate_videoclips(clips)

        # Set the fps for the audio
        final_clip.audio.fps = 44100

        """

        audiofile_path = fr"output\finalvideo\audio_{i}.wav"

        final_clip.audio.write_audiofile(audiofile_path)

        silence_detect(audiofile_path, f'silence_data_{i}.csv')

        silence_cuts = f'output/finalvideo/silence/silence_data_{i}.csv'

        

        if os.path.exists(silence_cuts):

            clips = []

            # Keep track of the end of the last silence period
            last_end = 0

            # Load the CSV file
            silence_data = load_csv(silence_cuts)

            # Loop over the silence periods
            for silence in silence_data:
                # Make a new clip that starts at the end of the last silence period and ends at the start of this one
                new_clip = clip.subclip(last_end, float(silence['start_time']))
                clips.append(new_clip)

                # Update the end of the last silence period
                last_end = float(silence['end_time'])

            # Add the last part of the video, from the end of the last silence period to the end of the video
            clips.append(clip.subclip(last_end))

            # Combine all the new clips into the final video
            final_clip = concatenate_videoclips(clips)

        delete_file(audiofile_path)

        """

        # Write the final clip to a file with an index
        final_clip.write_videofile(
            fr"C:\Users\Akshat Kumar\AI\YT Creator\output\finalvideo\video_{i}.mp4", 
            codec='h264_nvenc', 
            preset='ll', 
            threads=16,
            ffmpeg_params=['-movflags', '+faststart']
        )


    # Close the video file
    source_video.close()

editvideo("input/RP insulin.mp4", cutstamp_path="output/cutstamp", srt_path="output/transcribe/RP insulin.srt", num_videos=4)