import os
import subprocess

def download(url, output, file_name=None):
    # Create the directory if it does not exist
    os.makedirs(output, exist_ok=True)

    # Get the video title if file_name is not provided
    if file_name is None:
        title_command = f"yt-dlp -q --get-title {url}"
        file_name = subprocess.getoutput(title_command)

    # Replace characters that might be invalid in a file name
    file_name = file_name.replace('|', '-').replace('/', '-').replace(':', '-').replace('?', '-')

    # Name audio file
    audio_filename = f"{output}{file_name}_audio.m4a"

    # Check if the file exists and delete it
    if os.path.exists(audio_filename):
        os.remove(audio_filename)
    
    # Download audio
    audio_command = f"yt-dlp -q -x -f bestaudio[ext=m4a] {url} -o \"{audio_filename}\""
    os.system(audio_command)

    print("Audio saved in directory:", os.path.dirname(audio_filename))

    return audio_filename

def download_video_and_audio(url, output, file_name=None):
    # Create the directory if it does not exist
    os.makedirs(output, exist_ok=True)

    # Get the video title if file_name is not provided
    if file_name is None:
        title_command = f"yt-dlp -q --get-title {url}"
        file_name = subprocess.getoutput(title_command)

    # Replace characters that might be invalid in a file name
    file_name = file_name.replace('|', '-').replace('/', '-').replace(':', '-').replace('?', '-')

    file_path = os.path.join(output, file_name)
    # Name video file
    video_filename = f"{file_path}.mp4"

    # Check if the file exists and delete it
    if os.path.exists(video_filename):
        os.remove(video_filename)
    
    # Download video
    video_command = f"yt-dlp -q -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4] {url} -o \"{video_filename}\""
    os.system(video_command)

    print("Video saved in directory:", os.path.dirname(video_filename))

    # Replace backslashes with forward slashes for compatibility
    video_filename = video_filename.replace('\\', '/')

    return video_filename

if __name__ == '__main__':
    file_saved = download_video_and_audio("https://www.youtube.com/watch?v=dQw4w9WgXcQ", r"C:\\Users\\Akshat Kumar\AI\\YT Creator\\myproject\\projects\\project_1\\input\\")
    print("File saved in directory:", os.path.dirname(file_saved))