import sys
from nltk import word_tokenize, sent_tokenize
from nltk import FreqDist
from nltk.corpus import stopwords
from nltk.tokenize import MWETokenizer
stop_words = set(stopwords.words('english'))
import spacy
import re
import math

KEEP_ENTS = ['DATE', 'PERSON', 'GPE', 'ORG', 'NORP', 'WORK_OF_ART', 'PRODUCT']

class EntityRetokenizeComponent:
    def __init__(self, nlp):
        pass

    def __call__(self, doc):
        with doc.retokenize() as retokenizer:
            for ent in doc.ents:
                if ent in KEEP_ENTS:
                    retokenizer.merge(doc[ent.start:ent.end])
        return doc

nlp = spacy.load('en_core_web_sm')
retokenizer = EntityRetokenizeComponent(nlp)
nlp.tokenizer.rules = {key: value for key, value in nlp.tokenizer.rules.items() if "'" not in key and "’" not in key and "‘" not in key}
assert [t.text for t in nlp("can't")] == ["can't"]

def read_file(filepath):
    f = open(filepath, 'r')
    return f.read()
    
word_freq = {}
word_freq_file = 'word_freq.txt'
with open(word_freq_file, encoding="utf-8") as f:
    for line in f:
        word, freq = line.strip().split()
        word_freq[word] = float(freq)

class Word:
    def __init__(self, word, tf=None, idf=None):
        self.word = word
        self.tf = tf
        self.idf = idf 
        self.tfidf = tf * idf if tf and idf else None

    def __str__(self):
        out = 'Word: {}, tf: {}, idf: {}, tfidf: {}'.format(self.word, self.tf, self.idf, self.tfidf)
        return out

class TFIDF:

    def __init__(self, text):
        self.text = text
        self.num_words = None
        self.words = {} 

    def most_common_words(self):
        num_words = 0
        ent_list = []
        doc = nlp(text)

        with doc.retokenize() as retokenizer:
            for ent in doc.ents:
                if ent.label_ in KEEP_ENTS:
                    ent_list.append(ent.text.lower())
                    retokenizer.merge(doc[ent.start:ent.end])

        cleaned_words = []

        for w in doc:
            num_words += 1
            word = w.text.lower()
            if word not in stop_words and word not in """,.'"!?;:`~--()\n\n""" and word not in ent_list:
                cleaned_words.append(word) 

        self.num_words = num_words
        fqdst = FreqDist(cleaned_words)
        for word, val in fqdst.most_common():
            tf = val / num_words
            if word not in word_freq:
                continue
            print(word)
            print(word_freq[word])
            idf = math.log(word_freq[word]) + 10
            wd = Word(word, tf=tf, idf=idf)
            self.words[word] = wd
        self.freq_dist = fqdst
        for key, val in self.words.items():
            print(val)
        return fqdst

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
    tfidf = TFIDF(text)
    tfidf.most_common_words()