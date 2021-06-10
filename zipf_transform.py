from synonyms import get_synonyms
from collections import defaultdict
import math
import re
import spacy
import sys
import os
from nltk import word_tokenize, sent_tokenize
from nltk import FreqDist
from nltk.corpus import stopwords
from nltk.tokenize import MWETokenizer
import time
import random
stop_words = set(stopwords.words('english'))
import lemminflect
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
nlp.tokenizer.rules = {key: value for key, value in nlp.tokenizer.rules.items(
) if "'" not in key and "’" not in key and "‘" not in key}
assert [t.text for t in nlp("can't")] == ["can't"]


def read_file(filepath):
    f = open(filepath, 'r')
    return f.read()


word_freq = {}
word_freq_file = 'tfidf_freq.txt'
with open(word_freq_file, encoding="utf-8") as f:
    for line in f:
        word, freq = line.strip().split()
        word_freq[word] = float(freq)


class Word:
    def __init__(self, word, tf=None, idf=None, pos=None):
        self.word = word
        self.tf = tf
        self.idf = idf
        self.tfidf = tf * idf if tf and idf else None
        self.pos = pos

    def __str__(self):
        out = 'Word: {}, tf: {}, idf: {}, tfidf: {}'.format(
            self.word, self.tf, self.idf, self.tfidf)
        return out


class Zipf:

    def __init__(self, text):
        self.text = text
        self.num_words = None
        self.words = {}
        self.freq_dist = None
        self.pos_dict = defaultdict(lambda: defaultdict(lambda: 0))
        self.generate()

    def generate(self):
        num_words = 0
        ent_list = []
        doc = nlp(self.text)

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
                cleaned_words.append((word, w.pos_))

        self.num_words = num_words
        fqdst = FreqDist()
        for word, pos in cleaned_words:
            fqdst[word] += 1
            self.pos_dict[word][pos] += 1
        for word, val in fqdst.most_common():
            tf = val / num_words
            if word not in word_freq:
                continue
            idf = word_freq[word]
            wd = Word(word, tf=tf, idf=idf)
            self.words[word] = wd
        self.freq_dist = fqdst
        return fqdst

    def sort(self):
        if not self.words:
            return []
        words = sorted(self.words.values(),
                       key=lambda x: x.tfidf, reverse=True)
        return words

    def most_common(self):
        return self.freq_dist.most_common()

    def word_count(self):
        count = defaultdict(lambda: 0)
        words = self.most_common()
        for word in words:
            count[word] += 1
        return count

    def generate_random(self):
        return int.from_bytes(os.urandom(8), byteorder="big") / ((1 << 64) - 1)

    def inflect(self, word, tag):
        doc = nlp(word)
        word_sub = doc[0]._.inflect(tag)
        return word_sub
    
    def transform(self, rate=0.5, word_pct=0.1):
        words = self.sort()
        counts = self.word_count
        doc = nlp(self.text)
        text = self.text
        new_text = ''
        old_text = text
        max_words = int(word_pct * len(words))
        for i, wordObj in enumerate(words):
            if i > max_words:
                break
            word = wordObj.word
            for tok in doc:
                if tok.text == word:
                    if self.generate_random() <= rate:
                        if word == 'said':
                            synonyms=['uttered', 'declared', 'spoke', 'reported']
                            text = text.replace(word, random.choice(synonyms), 1)
                        else:
                            synonyms=get_synonyms(tok.text, tok.pos_)
                        if not synonyms:
                            continue
                        else:
                            synonym = random.choice(synonyms)
                            synonym = synonym.replace('_', ' ')
                            replacement = self.inflect(synonym, tok.tag_)
                            text=text.replace(word, replacement, 1)
                    else:
                        cut = text.split(word, 1)
                        if len(cut) != 1:
                            new_text += cut[0] + word
                            text = cut[1]
            text = new_text + text 
            new_text = ''
        return text

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please specify a file.')
        sys.exit()
    filename=sys.argv[1]
    text=read_file(filename)
    tfidf=Zipf(text)
    order_1=tfidf.sort()
    out=tfidf.transform(rate=0.7, word_pct=.4)
    print(out)
