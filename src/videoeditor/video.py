from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, ImageClip
from moviepy.config import change_settings
from silencedetect import silence_detect
import glob
from utils import *

change_settings({"IMAGEMAGICK_BINARY": r"c:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

class Video:
    def __init__(self, video_path, srt_path):
        self.source_video = VideoFileClip(video_path)
        self.timebase = 1 / self.source_video.fps
        self.caption_df = parse_srt(srt_path)
        self.offset = 0

    def edit(self, cutstamp_path, num_videos):
        caption_starts = [convert_srt_to_secs(t) - self.offset for t in self.caption_df['start']] 
        caption_ends = [convert_srt_to_secs(t) - self.offset for t in self.caption_df['end']] 
        captions = self.caption_df['caption'].tolist()

        # Get a list of all CSV files
        csv_files = glob.glob(f'{cutstamp_path}/short_*.csv')[:num_videos]

        # Main Loop to create videos
        for i, csv_file in enumerate(csv_files, 1):
            # Read the CSV file
            df = pd.read_csv(csv_file)

            starts = df.iloc[:, 0]  # First column
            ends = df.iloc[:, 1]  # Second column

            clips = []

            # Loop over all rows in the CSV file
            for start, end in zip(starts, ends):
                # Convert timestamps to seconds, create a subclip and add it to the list
                start_sec = convert_to_seconds(start, self.timebase)
                end_sec = convert_to_seconds(end, self.timebase)
                clip = self.source_video.subclip(seconds_to_time(start_sec), seconds_to_time(end_sec))

                # Find all captions that fall within the clip
                clip_captions = [(c_start, c_end, caption) for c_start, c_end, caption in zip(caption_starts, caption_ends, captions) if c_start >= start_sec and c_end <= end_sec]

                # Create an image and a text clip for each caption and add it to a list
                txt_clips = [ImageClip(make_text_image(caption), duration=c_end-c_start).set_start(c_start - start_sec).set_pos('bottom') for c_start, c_end, caption in clip_captions]

                # Add the original clip to the list of text clips
                txt_clips.insert(0, clip)

                # Combine the clip with all text clips
                clip = CompositeVideoClip(txt_clips)

                clips.append(clip)

            # Concatenate all clips together
            final_clip = concatenate_videoclips(clips)

            # Set the fps for the audio
            final_clip.audio.fps = 44100

            audiofile_path = fr"output\finalvideo\audio_{i}.wav"

            final_clip.audio.write_audiofile(audiofile_path)

            silence_detect(audiofile_path, f'silence_data_{i}.csv')

            silence_cuts = f'output/finalvideo/silence/silence_data_{i}.csv'

            if os.path.exists(silence_cuts):

                clips = []

                # Keep track of the end of the last silence period
                last_end = 0

                # Load the CSV file
                silence_data = load_csv(silence_cuts)

                # Loop over the silence periods
                for silence in silence_data:
                    # Make a new clip that starts at the end of the last silence period and ends at the start of this one
                    new_clip = clip.subclip(last_end, float(silence['start_time']))
                    clips.append(new_clip)

                    # Update the end of the last silence period
                    last_end = float(silence['end_time'])

                # Add the last part of the video, from the end of the last silence period to the end of the video
                clips.append(clip.subclip(last_end))

                # Combine all the new clips into the final video
                final_clip = concatenate_videoclips(clips)

            delete_file(audiofile_path)

            # Write the final clip to a file with an index
            final_clip.write_videofile(
                fr"C:\Users\Akshat Kumar\AI\YT Creator\output\finalvideo\video_{i}.mp4", 
                codec='h264_nvenc', 
                preset='ll', 
                threads=16,
                ffmpeg_params=['-movflags', '+faststart']
            )


        # Close the video file
        self.source_video.close()

    def process_all_videos(self, cutstamp_path, num_videos):
        pass
