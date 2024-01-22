import json
import os
from src import config
from src.setup_project import setup_project
from src.youtube.videodownloader import download, download_video_and_audio
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
video_file = download_video_and_audio(url, config.react_public_folder_path, config.project_name)

whisperx.transcribe(audio_file, config.transcript_folder, speakers=1)

response = generate_response(config.cutstamp_folder, config.words_path, video_file)

with open("testResponse(new).json", 'w') as outfile:
    json.dump(response, outfile, indent=4)

"""
gpt.gen_cutstamps(config.trs_path)
video = Video(video_path=config.video, srt_path=config.srt_path)
video.edit(config.cutstamp_folder, num_videos=3) """