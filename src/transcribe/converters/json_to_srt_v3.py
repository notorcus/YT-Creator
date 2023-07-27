import json
from datetime import timedelta

def fill_missing_times(word, previous_word, next_word, last_word_end, next_word_start):
    if 'start' not in word and last_word_end is not None:
        word['start'] = last_word_end + 0.005
    if 'end' not in word and next_word_start is not None:
        word['end'] = next_word_start - 0.005
    if previous_word and 'end' in previous_word:
        word['start'] = previous_word['end'] + 0.005
    if next_word and 'start' in next_word:
        word['end'] = next_word['start'] - 0.005
    return word

def fill_all_missing_times(data):
    for entry_index, entry in enumerate(data):
        for word_index, word in enumerate(entry.get('words', [])):
            previous_word = entry['words'][word_index - 1] if word_index > 0 else None
            next_word = entry['words'][word_index + 1] if word_index < len(entry['words']) - 1 else None
            last_word_end = data[entry_index - 1]['words'][-1]['end'] if entry_index > 0 else None
            next_word_start = data[entry_index + 1]['words'][0]['start'] if entry_index < len(data) - 1 else None
            word = fill_missing_times(word, previous_word, next_word, last_word_end, next_word_start)

def generate_subtitles_for_text(words, min_duration, max_char_length):
    groups = []
    current_group = []
    current_duration = 0.0
    current_length = 0

    min_char_length = max_char_length // 2

    for word in words:
        word_text = word['word']
        word_start = word['start']
        word_end = word['end']
        word_duration = word_end - word_start
        word_length = len(word_text)

        if (current_length + word_length > max_char_length and current_length >= min_char_length) or \
           (current_duration + word_duration > min_duration and current_length >= min_char_length):
            if current_group:
                groups.append({
                    'text': ' '.join([word['word'] for word in current_group]),
                    'start': current_group[0]['start'],
                    'end': current_group[-1]['end']
                })
            current_group = [word]
            current_duration = word_duration
            current_length = word_length
        else:
            current_group.append(word)
            current_duration += word_duration
            current_length += word_length + 1  # +1 for the space between words

    if current_group:
        groups.append({
            'text': ' '.join([word['word'] for word in current_group]),
            'start': current_group[0]['start'],
            'end': current_group[-1]['end']
        })

    # Post-processing: Ensure all groups have at least min_char_length characters
    for i in range(len(groups)):
        while len(groups[i]['text']) < min_char_length:
            if i > 0 and len(groups[i - 1]['text']) > min_char_length:
                # Borrow from the previous group
                prev_group_words = groups[i - 1]['text'].split()
                borrowed_word = prev_group_words.pop()
                groups[i - 1]['text'] = ' '.join(prev_group_words)
                groups[i]['text'] = borrowed_word + ' ' + groups[i]['text']
            elif i < len(groups) - 1 and len(groups[i + 1]['text']) > min_char_length:
                # Borrow from the next group
                next_group_words = groups[i + 1]['text'].split()
                borrowed_word = next_group_words.pop(0)
                groups[i + 1]['text'] = ' '.join(next_group_words)
                groups[i]['text'] += ' ' + borrowed_word
            else:
                # Can't borrow from either group, break the loop
                break

    # Post-processing: Remove gaps between groups
    for i in range(len(groups) - 1):
        current_group_end = groups[i]['end']
        next_group_start = groups[i + 1]['start']
        if current_group_end < next_group_start:
            avg_time = (current_group_end + next_group_start) / 2
            groups[i]['end'] = avg_time
            groups[i + 1]['start'] = avg_time

    return groups

def generate_subtitles(data, min_duration, max_char_length):
    subtitles = []
    for entry in data:
        subtitles += generate_subtitles_for_text(entry['words'], min_duration, max_char_length)

    # Post-processing: Remove gaps between subtitles
    for i in range(len(subtitles) - 1):
        current_subtitle_end = subtitles[i]['end']
        next_subtitle_start = subtitles[i + 1]['start']
        if current_subtitle_end < next_subtitle_start:
            avg_time = (current_subtitle_end + next_subtitle_start) / 2
            subtitles[i]['end'] = avg_time
            subtitles[i + 1]['start'] = avg_time

    return subtitles

def to_srt_time(seconds):
    return str(timedelta(seconds=seconds))

def save_to_srt(subtitles, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for i, subtitle in enumerate(subtitles, 1):
            f.write(str(i) + '\n')
            f.write(to_srt_time(subtitle['start']) + " --> " + to_srt_time(subtitle['end']) + '\n')
            f.write(subtitle['text'] + '\n\n')

# Load your JSON file
with open("output/transcribe/RP insulin.json", 'r') as f:
    data = json.load(f)

# Fill missing 'start' and 'end' keys
fill_all_missing_times(data)

# Generate subtitles
subtitles = generate_subtitles(data, min_duration=1.5, max_char_length=25)

# Save to SRT file
save_to_srt(subtitles, "output/transcribe/RP insulin(new).srt")
