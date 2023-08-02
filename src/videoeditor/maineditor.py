from video import Video

def main():
    video_path = "input/RP insulin.mp4"
    srt_path = "output/transcribe/RP insulin.srt"
    cutstamp_path = "output/cutstamp"
    num_videos = 2

    video = Video(video_path, srt_path)
    video.edit_video(cutstamp_path, num_videos)

if __name__ == "__main__":
    main()