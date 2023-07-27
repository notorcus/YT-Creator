import os
import whisperx
from moviepy.editor import VideoFileClip
from transcribe.converters.json_to_srt_v1 import convert_to_srt
from transcribe.converters.json_to_transcript import convert_to_transcript

output_path = ""
srt_output_path = ""
transcript_output_path = ""


def get_filename(filepath):
    filename = os.path.basename(filepath)
    filename_without_extension = os.path.splitext(filename)[0]
    return filename_without_extension

def extract_audio(video_path, audio_filename="audio.wav"):
    video_clip = VideoFileClip(video_path)

    # Get the directory of the video file
    video_dir = os.path.dirname(video_path)

    # Construct the full audio file path
    audio_path = os.path.join(video_dir, audio_filename)

    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_path)

    # Return the path of the audio file
    return audio_path

def transcribe(audio_file, speakers: int, language="en", device="cuda", model_name="large-v2", batch_size=16, compute_type="float16"):
    global output_path, srt_output_path, transcript_output_path

    audio_file = extract_audio(audio_file, f"{get_filename(audio_file)}.wav")

    model = whisperx.load_model(model_name, device, compute_type=compute_type, language=language)
    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio, batch_size=batch_size)
    print("Transcribed")

    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
    print("Stamps Aligned")

    if speakers > 1:
        diarize_model = whisperx.DiarizationPipeline(use_auth_token='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', device=device)
        diarize_segments = diarize_model(audio_file, min_speakers=1, max_speakers=speakers)
        result = whisperx.assign_word_speakers(diarize_segments, result)
        print("Diarized")

    import json

    output_path = fr"C:\Users\Akshat Kumar\AI\YT Creator\output\transcribe\{get_filename(audio_file)}.json"
    srt_output_path = fr"C:\Users\Akshat Kumar\AI\YT Creator\output\transcribe\{get_filename(audio_file)}.srt"
    transcript_output_path = fr"C:\Users\Akshat Kumar\AI\YT Creator\output\transcribe\{get_filename(audio_file)}_transcript.txt"

    with open(output_path, "w") as outfile:
        json.dump(result["segments"], outfile)

    convert_to_srt(output_path, srt_output_path)
    convert_to_transcript(output_path, transcript_output_path, speaker=speakers)

    print("Files Created")