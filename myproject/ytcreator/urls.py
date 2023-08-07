from django.urls import path
from .views import download_video

urlpatterns = [
    path('api/download_video', download_video),
]