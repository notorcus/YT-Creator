import os, config
from setup_project import setup_project
from youtube.videodownloader import download
from transcribe import maintranscribe as whisperx
from shortgen import gpt
# from videoeditor.video import Video

# config.project_name = input("Project Name: ")
config.project_name = "test"
setup_project(config.project_name)

# url = input("Youtube video URL: ")
url = "https://youtu.be/sA36RIv1A_k"

audio_file = download(url, output = os.path.join(config.project_dir, "input/"), file_name = config.project_name)

whisperx.transcribe(audio_file, speakers=1)

gpt.gen_cutstamps(config.trs_path)

"""

video = Video(video_path=file, srt_path=whisperx.srt_output_path)
video.edit(cutstamp_path, num_videos)

"""