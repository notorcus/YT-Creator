import csv
import subprocess
import re

def detect(filename, noise_level="-30dB", silence_duration="0.35"):
    command = [
        'ffmpeg',
        '-i', filename,
        '-af', f'silencedetect=n={noise_level}:d={silence_duration}',
        '-f', 'null', '-'
    ]
    result = subprocess.run(command, capture_output=True, text=True)

    # Only keep lines that contain 'silence_start' or 'silence_end'
    lines = result.stderr.split('\n')
    filtered_output = [line for line in lines if 'silence_start' in line or 'silence_end' in line]

    return '\n'.join(filtered_output)

def parse_output(output):
    lines = output.split('\n')
    silence_data = []
    for line in lines:
        if "silence_start" in line:
            start_time = float(re.search(r"silence_start: ([-+]?\d*\.\d+|\d+)", line).group(1))
        if "silence_end" in line:
            end_time = float(re.search(r"silence_end: ([-+]?\d*\.\d+|\d+)", line).group(1))
            duration = float(re.search(r"silence_duration: ([-+]?\d*\.\d+|\d+)", line).group(1))
            silence_data.append({'start_time': start_time, 'end_time': end_time, 'duration': duration})
    return silence_data

def save_to_csv(data, filename):
    if data:  # check if the list is not empty
        keys = data[0].keys()
        with open(filename, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
    else:
        print('No silence detected in the audio file.')

def silence_detect(input_filename, output_filename):
    stderr_output = detect(input_filename)
    silence_data = parse_output(stderr_output)
    save_to_csv(silence_data, fr"output\finalvideo\silence\{output_filename}")