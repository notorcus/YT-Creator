import os
from .. import config
import whisperx
from .converters.json_to_srt import convert_to_srt
from .converters.json_to_transcript import convert_to_transcript



def get_filename(filepath):
    filename = os.path.basename(filepath)
    filename_without_extension = os.path.splitext(filename)[0]
    return filename_without_extension

def transcribe(audio_file, speakers: int, language="en", device="cuda", model_name="large-v2", batch_size=16, compute_type="float16"):

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

    abs_transcript_folder = os.path.abspath(config.transcript_folder)
    config.json_path = os.path.join(abs_transcript_folder, f"{get_filename(audio_file)}.json")
    config.srt_path = os.path.join(abs_transcript_folder, f"{get_filename(audio_file)}.srt")
    config.trs_path = os.path.join(abs_transcript_folder, f"{get_filename(audio_file)}_transcript.txt")

    print("folder path: ", abs_transcript_folder)
    print("json path: ", config.srt_path)
    print("srt path: ", config.srt_path)
    print("trs path: ", config.trs_path)

    import json

    with open(config.json_path, "w") as outfile:
        json.dump(result["segments"], outfile)

    convert_to_srt(config.json_path, config.srt_path)
    convert_to_transcript(config.json_path, config.trs_path, speaker=speakers)

    print("Files Created")