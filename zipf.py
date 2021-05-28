import sys
from nltk import word_tokenize, sent_tokenize
from nltk import FreqDist
from nltk.corpus import stopwords
from nltk.tokenize import MWETokenizer
stop_words = set(stopwords.words('english'))
import spacy
nlp = spacy.load('en_core_web_sm')
import re

# def create_regex(word):
#     return ('/([%s])/g' % word)

def read_file(filepath):
    f = open(filepath, 'r')
    return f.read()

def most_common_words(raw_text, entities):

    token_pairs = [tuple(e.split()) for e in entities]

    tokenizer = MWETokenizer(token_pairs, separator=' ')

    tokenized_words = word_tokenize(raw_text)

    cleaned_words = []

    for w in tokenized_words:
        w = w.lower()
        if w not in stop_words and w not in """,.'"!?;:`~--()""":
            cleaned_words.append(w)
    
    tokenized_words = tokenizer.tokenize(raw_text.split())

    fqdst = FreqDist(cleaned_words)

    return fqdst

KEEP_ENTS = ['DATE', 'PERSON', 'GPE', 'ORG', 'NORP', 'WORK_OF_ART', 'PRODUCT']
def tag_entities(text):
    ents = []
    doc = nlp(text)
    for token in doc.ents:
        if token.label_ in KEEP_ENTS:
            # print(token.text, token.label_)
            ents.append(token.text)
    return ents

def entity_tag(freq_dist):
    for word, count in freq_dist:
        doc = nlp(word)
        for token in doc.ents:
            print(token.label_)
            print(token.text)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please specify a file.')
        sys.exit()
    filename = sys.argv[1]
    text = read_file(filename)
    # entity_tag(common)
    ents = tag_entities(text)
    most_common_words(text, ents)
    CDFqdst = most_common_words(text, ents)
    common = CDFqdst.most_common(100)
    print(common)