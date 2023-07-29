import json
from datetime import timedelta

def convert_to_srt(json_filepath, srt_filepath, max_char_length=10, min_duration=1.5):
    with open(json_filepath) as file:
        data = json.load(file)

    srt_entries = []
    current_entry = {"start": None, "end": None, "texts": []}
    last_word_end = None
    next_word_start = None

    for entry_index, entry in enumerate(data):
        for word_index, word in enumerate(entry.get('words', [])):
            if 'start' not in word or 'end' not in word:
                previous_word = entry['words'][word_index - 1] if word_index > 0 else None
                next_word = entry['words'][word_index + 1] if word_index < len(entry['words']) - 1 else None

                if 'start' not in word and last_word_end is not None:
                    word['start'] = last_word_end + 0.005
                if 'end' not in word and next_word_start is not None:
                    word['end'] = next_word_start - 0.005

                if previous_word and 'end' in previous_word:
                    word['start'] = previous_word['end'] + 0.005
                if next_word and 'start' in next_word:
                    word['end'] = next_word['start'] - 0.005

            if not current_entry["texts"]:
                current_entry["start"] = word["start"]
                current_entry["end"] = word["end"]
                current_entry["texts"].append(word["word"])
            else:
                # Check if the last character of the word is an end punctuation mark
                ends_with_punctuation = word["word"][-1] in ['.', '?']

                if len(" ".join(current_entry["texts"])) + len(word["word"]) + 1 > max_char_length or word["start"] - current_entry["end"] >= min_duration or ends_with_punctuation:
                    srt_entries.append(current_entry)
                    current_entry = {"start": word["start"], "end": word["end"], "texts": [word["word"]]}
                else:
                    current_entry["end"] = word["end"]
                    current_entry["texts"].append(word["word"])

            if 'end' in word:
                last_word_end = word['end']

            if word_index == len(entry['words']) - 1 and entry_index < len(data) - 1:
                next_entry = data[entry_index + 1]
                if next_entry['words'] and 'start' in next_entry['words'][0]:
                    next_word_start = next_entry['words'][0]['start']

    if current_entry["texts"]:
        srt_entries.append(current_entry)

    srt_data = ""
    for i, entry in enumerate(srt_entries, start=1):
        start = timedelta(seconds=entry["start"])
        end = timedelta(seconds=entry["end"])
        texts = " ".join(entry["texts"])
        srt_data += f"{i}\\n{start} --> {end}\\n{texts}\\n\\n"

    with open(srt_filepath, 'w') as file:
        file.write(srt_data)
