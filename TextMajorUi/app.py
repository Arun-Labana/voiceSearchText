import os
import difflib
import nltk
from fuzzywuzzy import fuzz
from difflib import get_close_matches
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    query = request.form["query"]
    results = get_closest_match(query)
    return render_template("results.html", results=results)

def get_closest_match(query_word):
    def find_most_similar_word_in_file(file_path, query_word):
        with open(file_path, "r") as file:
            text = file.read()
            words = nltk.word_tokenize(text)
            most_similar_word_fuzzy = max(words, key=lambda word: fuzz.ratio(word.lower(), query_word.lower()))
            most_similar_word_diff = get_close_matches(query_word.lower(), [word.lower() for word in words])
            return most_similar_word_fuzzy, most_similar_word_diff

    transcriptions_folder = "../Transcriptions"
    similarity_scores = []
    for file_name in os.listdir(transcriptions_folder):
        file_path = os.path.join(transcriptions_folder, file_name)
        similar_word_fuzzy, similar_word_diff = find_most_similar_word_in_file(file_path, query_word)
        similarity_fuzzy = fuzz.ratio(similar_word_fuzzy.lower(), query_word.lower())
        similarity_diff = max([fuzz.ratio(similar_word.lower(), query_word.lower()) for similar_word in similar_word_diff], default=0)
        # Assign weight to prioritize results from difflib over fuzzywuzzy
        combined_similarity = similarity_diff * 2 + similarity_fuzzy
        similarity_scores.append((file_path, combined_similarity))

    top_5_results = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[:5]
    return top_5_results

def closet_match(query):
    transcriptions_folder = "../Transcriptions"
    transcription_files = os.listdir(transcriptions_folder)
    files = []
    for file_name in transcription_files:
        file_path = os.path.join(transcriptions_folder, file_name)
        with open(file_path, "r") as file:
            transcription = file.read()
            trans = transcription.split()
            words = difflib.get_close_matches(query, trans)
            if len(words) != 0:
                 files.append(file_name)
    return files

if __name__ == '__main__':
    app.run(debug=True, port=5001)
