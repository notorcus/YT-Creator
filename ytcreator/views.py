from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from src.youtube.videodownloader import download
from src.setup_project import setup_project
from src.transcribe import maintranscribe as whisperx
from src.responsegenerator import generate_response
from src import config
import os, json

def process_video_core(url, mode="production"):
    if mode == "frontend_dev":
        # Read the testResponse.json file
        with open("testResponse(new).json", 'r') as file:
            response_data = json.load(file)
        return response_data

    # Set up the project
    config.project_name = "project_1"
    setup_project(config.project_name)

    # Specify your output directory and file name
    audio_file = download(url, output=os.path.join(config.project_dir, "input/"), file_name=config.project_name)

    # Transcribe the audio file
    whisperx.transcribe(audio_file, config.transcript_folder, speakers=1)

    response_data = generate_response(config.cutstamp_folder, config.words_path)

    return response_data

@csrf_exempt
def process_video(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid method. Use POST instead.")

    data = json.loads(request.body.decode('utf-8'))

    mode = data.get('mode', 'production')  # Default mode is "production"
    url = data.get('video_url', '')  # Get the video URL

    # Check if the video URL is provided for production mode
    if mode == "production" and not url:
        return HttpResponseBadRequest("Video URL is missing")

    response_data = process_video_core(url, mode=mode)
    return JsonResponse(response_data)