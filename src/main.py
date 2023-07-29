from transcribe import maintranscribe
from shortgen import gpt
from videoeditor import maineditor as editor

file = r"input/RP insulin.mp4"
cutstamp_path = r"output/cutstamp"
num_videos = 4

maintranscribe.transcribe(audio_file=file, speakers=1)

gpt.gen_cutstamps(maintranscribe.transcript_output_path, num_videos=num_videos)

editor.editvideo(file, cutstamp_path=cutstamp_path, srt_path=maintranscribe.srt_output_path, num_videos=num_videos)