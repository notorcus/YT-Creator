from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from src.youtube.videodownloader import download
from src.setup_project import setup_project
from src.transcribe import maintranscribe as whisperx
from src import config
import os, json

def process_video_core(url, mode="production"):
    # Set up the project
    config.project_name = "project_1"
    setup_project(config.project_name)

    # Specify your output directory and file name
    audio_file = download(url, output=os.path.join(config.project_dir, "input/"), file_name=config.project_name)

    # Transcribe the audio file
    whisperx.transcribe(audio_file, speakers=1)

    # Use the json_path from config
    transcript_path = config.json_path
    
    # Read and parse the transcript
    with open(transcript_path, 'r') as file:
        transcript_data = json.load(file)

    response_data = {
        "status": "success",
        "message": "Videos processed successfully.",
        "data": {
            "videos": [
                {
                    "start_time": "00:00:05", 
                    "end_time": "00:00:30",
                },
                {
                    "start_time": "00:01:21", 
                    "end_time": "00:02:07",
                },
                {
                    "start_time": "00:03:02", 
                    "end_time": "00:04:19",
                },
            ],
            "transcript": transcript_data
        }
    }      

    if mode == "cli":
        print(response_data)
        return
    else:
        return response_data

@csrf_exempt
def process_video(request):
    if request.method == 'POST':
        url = request.POST['video_url']
        response_data = process_video_core(url)
        return JsonResponse(response_data)
    else:
        return HttpResponseBadRequest("Invalid method. Use POST instead.")

if __name__ == '__main__':
    url = input("Enter the video URL: ")
    process_video_core(url, mode="cli")
