import json

# create a dictionary mapping from speaker labels to speaker names
speaker_mapping = {
    "SPEAKER_00": "Speaker 1",
    "SPEAKER_01": "Speaker 2"
    # add more speakers if needed
}

def seconds_to_time_format(seconds):
    # Convert seconds into HH:MM:SS format
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def convert_json_to_transcript(data, speaker: int):
    # Convert JSON data into the desired transcript format
    transcript = []
    for entry in data:
        start_time = seconds_to_time_format(entry['start'])
        end_time = seconds_to_time_format(entry['end'])
        
        # Check if 'speaker' key is in the entry
        if 'speaker' in entry:
            speaker_label = entry['speaker']
            # If the speaker label is not in the mapping, add it with a default name
            if speaker_label not in speaker_mapping:
                speaker_mapping[speaker_label] = f"Speaker {len(speaker_mapping) + 1}"
            speaker = speaker_mapping[speaker_label]
        else:
            if speaker == 1:
                speaker = "Speaker"
                
        text = entry['text'].strip()
        transcript.append(f"{speaker} ({start_time}-{end_time}): {text}")
    return "\n\n".join(transcript)


def convert_to_transcript(json_filepath, txt_filepath, speaker: int):
    # Load the JSON file
    with open(json_filepath) as file:
        data = json.load(file)

    # Convert the loaded JSON data into the desired format
    transcript = convert_json_to_transcript(data, speaker)

    # Write the transcript to an output file
    with open(txt_filepath, "w") as file:
        file.write(transcript)

if __name__ == '__main__':
    convert_to_transcript(r"projects\Goggins\intermediate\transcripts\MW Goggins.json", r"projects\Goggins\intermediate\transcripts\MW_Goggins_transcript.txt", speaker=2)