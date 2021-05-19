import sys
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet as wn
import re
from collections import Counter, defaultdict
import spacy
import time
import synonyms

nlp = spacy.load('en_core_web_sm')

reg_string = '([\w\-\s]+)\w+'

# ADJ - Adjective
# ADV - Adverb
# NOUN - Noun
# PRON - Pronoun
# PROPN - Proper noun
# SYM - Symbol
# VERB - Verb

SPACY_TAGS = ['ADJ', 'ADV', 'NOUN', 'VERB']

FANBOYS = ['for', 'and', 'nor', 'but', 'or', 'yet', 'so']

SCORE_CONSTANT = 206.835

def calculate_score(score_data):
    """
    Calculates the flesch reading score for a document given score_data
    Args:
        score_data (dict): A dictionary containing the variables necessary to calculate the flesch
        reading score.
        num_words: the number of words in a document
        num_sentences: the number of sentences in a document
        num_syllables: the number of syllables in the document
    Returns:
        float: A float of the Flesch Reading Score.
    """
    asl = score_data['num_words'] / score_data['num_sentences']
    asw = score_data['num_syllables'] / score_data['num_words']
    return SCORE_CONSTANT - (1.015 * asl) - (84.6 * asw)

def reduce_syllables(text, score_data=None, target=None):
    """
    Reduces the syllables from a text, starts by reducing the biggest words (most syllables).
    Args:
        text (string): The text of a document
        score_data (dict, optional): A dictionary containing score data. See above method. Defaults to None.
        target (float, optional): A target flesch reading score to hit. Defaults to None.
    """
    flesch_score = None
    doc = nlp(text)
    no_stopwords = []
    for token in doc:
        if token.text not in stopwords.words():
            # Special case for verbs, get the tense
            #if token.tag_[0] == 'V':
                #no_stopwords.append((token.text, token.pos_, token.tag_))
            no_stopwords.append((token.text, token.pos_))
    big_words = []
    for word, pos in no_stopwords:
        if re.search(r'([\w\-\s]+)\w+', word):
            big_words.append((word, pos, get_syllables(word)))
    big_words = sorted(big_words, key=lambda x: x[2], reverse=True)
    for word, pos, syl_count in big_words:
        if pos not in SPACY_TAGS:
            continue
        syns = get_synonyms(word, pos)
        print(syns)
        # print(names)
        transforms = [(n.split('.')[0], get_syllables(n.split('.')[0])) for n in names]
        for word_sub, syl_num in transforms:
            word_sub = word_sub.replace('_', ' ')
            if syl_num < syl_count:
                print('Replacement: {} ({}) -> {}'.format(word, pos[0], word_sub))
                text = text.replace(word, word_sub, 1)
                if score_data:
                    score_data['num_syllables'] -= (syl_count - syl_num)
                    flesch_score = calculate_score(score_data)
                    print('NEW SCORE:', flesch_score)
                break
        if target and flesch_score:
            if flesch_score > target:
                # print(text)
                return
    print(text)

def reduce_sentences(text, score_data=None, target=None):
    doc = nlp(text)
    for sent in doc.sents:
        if not sent:
            continue
        
        time.sleep(1)

def get_synonyms(word, pos):
    """Gets the synonym for a word.

    Args:
        word (string): The word to get a synonym for
        pos (string): The part of speech of the given word

    Returns:
        list[synset]: Returns a list of wordnet synsets for a given word.
    """
    return synonyms.get_synonyms(word, pos) 
    #return wn.synsets(word, pos=pos_to_wordnet_pos(pos))

def pos_to_wordnet_pos(spacy_tag, returnNone=False):
    """Converts a spacy POS tag to a wordnet POS tag.

    Args:
        spacy_tag (string): A spacy tag
        returnNone (bool, optional): [description]. Defaults to False.

    Returns:
        string: Returns a wordnet POS tag
    """
    spacy_to_wn = {
        'ADJ': 'a',
        'VERB': 'v',
        'NOUN': 'n',
        'ADV': 'r',
    }

    if spacy_tag in spacy_to_wn:
        return spacy_to_wn[spacy_tag]
    else:
        return 'n'

def get_syllables(word):
    """Gets the number of syllables in a word. It doesn't work that well, it might
    need to be improved in the future

    Args:
        word (string): A word

    Returns:
        int: The number of syllables in that word.
    """
    if not word:
        return -1
    count = 0
    vowels = 'aeiouy'
    word = word.lower()
    if word[0] in vowels:
        count +=1
    for index in range(1,len(word)):
        if word[index] in vowels and word[index-1] not in vowels:
            count +=1
    if word.endswith('e'):
        count -= 1
    if word.endswith('le'):
        count += 1
    if count == 0:
        count += 1
    return count


def flesch_score(text):
    """Calculates the flesch reading score of a given document
    https://readabilityformulas.com/flesch-reading-ease-readability-formula.php

    Args:
        text (string): A document
    """
    SCORE_CONSTANT = 206.835
    num_syllables = 0
    num_words = 0
    # smoothing, may be needed it's hard to count number of sentences, and in testing sent_tokenize has
    # consistently undercounted sentences.
    num_sentences = 0
    sentences = nltk.sent_tokenize(text)
    for sentence in sentences:
        if sentence == '.':
            continue
        num_sentences += 1
        for word in nltk.word_tokenize(sentence):
            if re.search(r'([\w\-\s]+)\w+', word):
                num_words += 1
                num_syllables += get_syllables(word)
    asl = num_words / num_sentences
    asw = num_syllables / num_words
    ease_score = SCORE_CONSTANT - (1.015 * asl) - (84.6 * asw)
    print(num_words)
    print(num_sentences)
    print(num_syllables)
    print('Flesch reading score:', ease_score)
    return ease_score

def read_file(filepath):
    f = open(filepath, 'r')
    return f.read()

def calculate_ttr(text):
    words = defaultdict(lambda: 0)
    c = Counter()
    num_words = 0
    tokens = word_tokenize(text)
    no_stopwords = [word for word in tokens if not word in stopwords.words()]
    for word in no_stopwords:
        if re.search(r'([\w\-\s]+)\w+', word):
            num_words += 1
            words[word] += 1
    TTR = len(words.keys()) / num_words
    print(TTR)
    # common = sorted(words.items(), key=lambda x: x[1], reverse=True)

sample_score_data = {
    'num_words': 614,
    'num_sentences': 38,
    'num_syllables': 920
}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please specify a file.')
        sys.exit()
    filename = sys.argv[1]
    text = read_file(filename)
    # calculate_ttr(text)
    # flesch_score(text)
    reduce_syllables(text, sample_score_data, 70)
    # reduce_sentences(text)


