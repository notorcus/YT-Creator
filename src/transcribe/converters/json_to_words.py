import json

def filter_words(json_path, output_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    all_words = []
    for entry in data:
        all_words.extend(entry.get('words', []))
    
    with open(output_path, 'w') as outfile:
        json.dump(all_words, outfile)
