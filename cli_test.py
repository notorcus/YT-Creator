import json
import os
from src import config
from src.setup_project import setup_project
from src.youtube.videodownloader import download
from src.transcribe import maintranscribe as whisperx
from src.responsegenerator import generate_response
# from shortgen import gpt
# from videoeditor.video import Video

# config.project_name = input("Project Name: ")

config.project_name = "test new json"
setup_project(config.project_name)

# url = input("Youtube video URL: ")
url = "https://youtu.be/NjvwWiCYLl4"

audio_file = download(url, output = os.path.join(config.project_dir, "input/"), file_name = config.project_name)

whisperx.transcribe(audio_file, speakers=1)

# response = generate_response(csv_folder=r"projects\project_1\intermediate\cutstamps", transcript_words=r"projects\test new json\intermediate\transcripts\test new json_audio_words.json")
response = generate_response(config.cutstamp_folder, config.words_path)

with open("testResponse(new).json", 'w') as outfile:
    json.dump(response, outfile, indent=4)

""" gpt.gen_cutstamps(config.trs_path)
video = Video(video_path=config.video, srt_path=config.srt_path)
video.edit(config.cutstamp_folder, num_videos=3) """