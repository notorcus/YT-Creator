from django.urls import path
from .views import process_video, download_video

urlpatterns = [
    path('api/process_video', process_video),
    path('api/download_video', download_video),
]