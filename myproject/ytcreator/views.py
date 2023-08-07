from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from src.youtube.videodownloader import download

import os

@csrf_exempt
def download_video(request):
    if request.method == 'POST':
        url = request.POST['video_url']
        # specify your output directory and file name
        download(url, output="path/to/output/dir", file_name="file_name")
        return JsonResponse({"status": "success"})
