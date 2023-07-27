import json
from datetime import timedelta

def fill_missing_times(word, previous_word, next_word, last_word_end, next_word_start):
    # If 'start' key is still not filled, use the 'end' key from the last word of the previous entry
    if 'start' not in word and last_word_end is not None:
        word['start'] = last_word_end + 0.005

    # If 'end' key is still not filled, use the 'start' key from the next word of the next entry
    if 'end' not in word and next_word_start is not None:
        word['end'] = next_word_start - 0.005

    # Update the 'start' and 'end' keys based on the previous and next words within the same entry
    if previous_word and 'end' in previous_word:
        word['start'] = previous_word['end'] + 0.005
    if next_word and 'start' in next_word:
        word['end'] = next_word['start'] - 0.005

    return word

def convert_to_srt(json_filepath, srt_filepath, max_char_length=25, min_duration=1.5):
    # Load the JSON file
    with open(json_filepath) as file:
        data = json.load(file)

    # Initialize list for the SRT entries
    srt_entries = []
    current_entry = {"start": None, "end": None, "texts": []}
    last_word_end = None
    next_word_start = None

    # Iterate over the data
    for entry_index, entry in enumerate(data):
        # Fill missing 'start' and 'end' keys for words
        for word_index, word in enumerate(entry.get('words', [])):
            if 'start' not in word or 'end' not in word:
                # Get the previous and next words
                previous_word = entry['words'][word_index - 1] if word_index > 0 else None
                next_word = entry['words'][word_index + 1] if word_index < len(entry['words']) - 1 else None

                word = fill_missing_times(word, previous_word, next_word, last_word_end, next_word_start)

            # If the current entry is empty, add the word to it
            if not current_entry["texts"]:
                current_entry["start"] = word["start"]
                current_entry["end"] = word["end"]
                current_entry["texts"].append(word["word"])  # Use 'word' key
            else:
                # If adding the word to the current entry exceeds the maximum character length or if the time gap to the next word is greater than or equal to the minimum duration, add the current entry to the SRT entries and start a new entry with the word
                if len(" ".join(current_entry["texts"])) + len(word["word"]) + 1 > max_char_length or word["start"] - current_entry["end"] >= min_duration:  # +1 for space
                    srt_entries.append(current_entry)
                    current_entry = {"start": word["start"], "end": word["end"], "texts": [word["word"]]}  # Use 'word' key
                else:
                    # Otherwise, add the word to the current entry
                    current_entry["end"] = word["end"]
                    current_entry["texts"].append(word["word"])  # Use 'word' key

            # Update the last word end time
            if 'end' in word:
                last_word_end = word['end']

            # Update the next word start time if the current word is the last word in the entry
            if word_index == len(entry['words']) - 1 and entry_index < len(data) - 1:
                next_entry = data[entry_index + 1]
                if next_entry['words'] and 'start' in next_entry['words'][0]:
                    next_word_start = next_entry['words'][0]['start']


    # Add the last entry to the SRT entries
    if current_entry["texts"]:
        srt_entries.append(current_entry)

    # Convert the SRT entries to SRT format
    srt_data = ""
    for i, entry in enumerate(srt_entries, start=1):
        start = timedelta(seconds=entry["start"])
        end = timedelta(seconds=entry["end"])
        texts = " ".join(entry["texts"])
        srt_data += f"{i}\n{start} --> {end}\n{texts}\n\n"

    # Save the SRT data to the file
    with open(srt_filepath, 'w') as file:
        file.write(srt_data)

convert_to_srt("output/transcribe/RP insulin.json", "output/transcribe/RP insulin(new).srt")