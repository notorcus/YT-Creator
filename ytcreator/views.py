from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from src.youtube.videodownloader import download, download_video_and_audio
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
    config.project_name = "Production project test"
    setup_project(config.project_name)

    # Specify your output directory and file name
    audio_file = download(url, output=os.path.join(config.project_dir, "input/"), file_name=config.project_name)
    video_file = download_video_and_audio(url, config.react_public_folder_path, config.project_name)

    # Transcribe the audio file
    whisperx.transcribe(audio_file, config.transcript_folder, speakers=1)

    response_data = generate_response(config.cutstamp_folder, config.words_path, video_file)

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
    
@csrf_exempt
def download_video(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid method. Use POST instead.")

    data = json.loads(request.body.decode('utf-8'))
    url = data.get('video_url', '')
    

    if not url:
        return HttpResponseBadRequest("Video URL is missing")

    output_path = "C:\\Users\\Akshat Kumar\\Editing\\Media\\"

    # Download the video
    local_file_path = download_video_and_audio(url, output=output_path)

    response_data = {
        "status": "success",
        "message": "Video downloaded successfully.",
        "file_path": local_file_path
    }

    print(response_data)

    return JsonResponse(response_data)