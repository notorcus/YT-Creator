from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from src.youtube.videodownloader import download
from src.setup_project import setup_project
from src.transcribe import maintranscribe as whisperx
from src import config
import os

@csrf_exempt
def process_video(request):
    if request.method == 'POST':
        url = request.POST['video_url']

        # Set up the project
        config.project_name = "project_1"
        setup_project(config.project_name)

        # Specify your output directory and file name
        audio_file = download(url, output=os.path.join(config.project_dir, "input/"), file_name=config.project_name)

        # Transcribe the audio file
        whisperx.transcribe(audio_file, speakers=1)

        return JsonResponse({"status": "success"})
    else:
        return HttpResponseBadRequest("Invalid method. Use POST instead.")
