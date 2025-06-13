from flask import Flask, render_template, request, jsonify # type: ignore
import re
from collections import Counter

app = Flask(__name__)


# Your pre-existing functions here
def process_text(path):
    words = []
    with open(path) as f:
        file_name_data = f.read()
    file_name_data = file_name_data.lower()
    words = re.findall(r'\w+', file_name_data)
    return words

book_words = process_text("C:/big.txt")
vocab = set(book_words)

def get_count(words):
    word_count_dict = Counter(words)
    return word_count_dict

word_count_dict = get_count(book_words)

def occurr_prob(word_count_dict):
    probs = {}
    m = sum(word_count_dict.values())
    for key in word_count_dict:
        probs[key] = word_count_dict[key] / m
    return probs

prob_of_occurr = occurr_prob(word_count_dict)

def del_letter(word):
    del_letter = []
    for i in range(len(word)):
        del_letter.append(word[:i] + word[i+1:])
    return del_letter
def switch_letter(word):
    sw_letter = []
    for i in range(len(word) - 1):
        sw_letter.append(word[:i] + word[i+1] + word[i] + word[i+2:])
    return sw_letter

def replace_letter(word):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    repl_let = []
    for i in range(len(word)):
        for l in letters:
            repl_let.append(word[:i] + l + word[i+1:])
    return list(set(repl_let) - set([word]))

def insert_letter(word):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    ins_let = []
    for i in range(len(word) + 1):
        for l in letters:
            ins_let.append(word[:i] + l + word[i:])
    return ins_let
def edit_one_letter(word, allow_switches=True):
    edit_one_set = set()
    edit_one_set.update(del_letter(word))
    if allow_switches:
        edit_one_set.update(switch_letter(word))
    edit_one_set.update(replace_letter(word))
    edit_one_set.update(insert_letter(word))
    return edit_one_set

def edit_two_letter(word, allow_switches=True):
    edit_two_set = set()
    edit_one = edit_one_letter(word, allow_switches=allow_switches)
    for w in edit_one:
        edit_two_set.update(edit_one_letter(w, allow_switches=allow_switches))
    return edit_two_set

def get_correlations(word, probs, vocab, n=2):
    suggestions = list(
        (word in vocab and word) or 
        edit_one_letter(word).intersection(vocab) or 
        edit_two_letter(word).intersection(vocab)
    )
    n_best = sorted([[s, probs[s]] for s in suggestions], key=lambda x: x[1], reverse=True)
    return n_best

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spellcheck', methods=['POST'])
def spellcheck():
    data = request.json
    word = data['word']
    corrections = get_correlations(word, prob_of_occurr, vocab)
    return jsonify(corrections)

if __name__ == '__main__':

    app.run(debug=True)