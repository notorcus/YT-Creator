from django.urls import path
from .views import process_video

urlpatterns = [
    path('api/process_video', process_video),
]