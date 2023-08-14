import json

def fill_missing_times(word, previous_word, next_word, last_word_end, next_word_start):
    # If 'start' is not present in the word
    if 'start' not in word:
        if previous_word and 'end' in previous_word:
            word['start'] = previous_word['end'] + 0.005
        elif last_word_end is not None:
            word['start'] = last_word_end + 0.005

    # If 'end' is not present in the word
    if 'end' not in word:
        if next_word and 'start' in next_word:
            word['end'] = next_word['start'] - 0.005
        elif next_word_start is not None:
            word['end'] = next_word_start - 0.005

    return word

def fill_all_missing_times(data):
    for entry_index, entry in enumerate(data):
        for word_index, word in enumerate(entry.get('words', [])):
            previous_word = entry['words'][word_index - 1] if word_index > 0 else None
            next_word = entry['words'][word_index + 1] if word_index < len(entry['words']) - 1 else None
            last_word_end = data[entry_index - 1]['words'][-1]['end'] if entry_index > 0 else None
            next_word_start = data[entry_index + 1]['words'][0]['start'] if entry_index < len(data) - 1 else None
            word = fill_missing_times(word, previous_word, next_word, last_word_end, next_word_start)

    return data

if __name__ == "__main__":
    input_path = r"projects\test new json\intermediate\transcripts\test new json_audio.json"
    
    with open(input_path, 'r') as infile:
        data = json.load(infile)

    updated_data = fill_all_missing_times(data)

    # Saving the updated data back to the input file
    with open(input_path, 'w') as outfile:
        json.dump(updated_data, outfile, indent=4)