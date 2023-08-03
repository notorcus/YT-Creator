import os

def download(url, output, file_name):
    # Create the directory if it does not exist
    os.makedirs(output, exist_ok=True)

    # Download audio
    audio_filename = "{}{}_audio.m4a".format(output, file_name)
    audio_command = "yt-dlp -q -x -f bestaudio[ext=m4a] {} -o \"{}\"".format(url, audio_filename)
    os.system(audio_command)

    print("Audio saved in directory: ", os.path.dirname(audio_filename))

    return audio_filename

if __name__ == '__main__':
    file_saved = download("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "./downloads/", "my_video")
    print("File saved in directory:", os.path.dirname(file_saved))
