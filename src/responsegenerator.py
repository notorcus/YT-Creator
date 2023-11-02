import json, os, csv

def generate_response(csv_folder, transcript_words, video_path):
    with open(transcript_words, 'r') as file:
        transcript_data = json.load(file)

    video_times = get_video_times_from_csv(csv_folder)
    
    if not video_times:  # If there are no videos from CSV, create default videos
        video_times = create_default_videos()

    videos_data = []
    for video in video_times:
        start_time = video["start_time"]
        end_time = video["end_time"]

        start_idx, end_idx = find_closest_indices(transcript_data, start_time, end_time)
        
        video_data = {
            # "start_time": start_time,
            # "end_time": end_time,
            "start_idx": start_idx,
            "end_idx": end_idx
        }
        videos_data.append(video_data)

    response_data = {
        "status": "success",
        "message": "Videos processed successfully.",
        "video_path": video_path,
        "data": {
            "videos": videos_data,
            "transcript": transcript_data
        }
    }      

    return response_data


def find_closest_indices(transcript_words, start_time, end_time):
    words = transcript_words
    
    start_idx = min(range(len(words)), key=lambda i: abs(words[i]['start'] - start_time))
    end_idx = min(range(len(words)), key=lambda i: abs(words[i]['end'] - end_time))
    
    return start_idx, end_idx

def convert_to_seconds(timestamp, timebase=24):
    hh, mm, ss, ff = map(int, timestamp.split(':'))
    return hh * 3600 + mm * 60 + ss + ff / timebase

def get_video_times_from_csv(csv_folder):
    csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]
    video_times = []

    for file in csv_files:
        with open(os.path.join(csv_folder, file), 'r') as f:
            reader = csv.reader(f)
            next(reader, None)  # skip the headers
            for row in reader:
                start_time, end_time = [convert_to_seconds(t) for t in row]
                video_times.append({
                    "start_time": start_time,
                    "end_time": end_time
                })

    return video_times

def create_default_videos():
    # Here you can define your default videos with their start and end times
    default_videos = [
        {"start_time": 10, "end_time": 30}, 
        {"start_time": 20, "end_time": 60},
        {"start_time": 60, "end_time": 100}
    ]
    return default_videos

if __name__ == "__main__":
    response = generate_response(csv_folder=r"projects\project_1\intermediate\cutstamps", transcript_words=r"projects\project_1\intermediate\transcripts\transcript_words.json")
    with open("testResponse(new).json", 'w') as file:
        json.dump(response, file, indent=4)