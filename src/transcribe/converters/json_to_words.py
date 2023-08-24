import json

def filter_words(json_path, output_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    all_words = []
    for entry in data:
        all_words.extend(entry.get('words', []))
    
    with open(output_path, 'w') as outfile:
        json.dump(all_words, outfile)

if __name__ == "__main__":
    filter_words(r"projects\Goggins\intermediate\transcripts\MW Goggins.json", r"projects\Goggins\intermediate\transcripts\MW Goggins_words.json")