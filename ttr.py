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
import lemminflect

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

def sort_words(text, reverse_order=True):
    """Parses and sorts words in a document

    Args:
        text (str): A document
        reverse_order (bool, optional): This will order the words from the most syllables to the least. Defaults to True.

    Returns:

        (word, Part of Speech, # Syllables, spacy tag): A tuple containing a bunch of information about a word
    """
    doc = nlp(text)
    no_stopwords = []
    for token in doc:
        if token.text not in stopwords.words():
            # Special case for verbs, get the tense
            no_stopwords.append((token.text, token.pos_, token.tag_))
    big_words = []
    for word, pos, tok_tag in no_stopwords:
        if re.search(r'([\w\-\s]+)\w+', word):
            big_words.append((word, pos, get_syllables(word), tok_tag))
    big_words = sorted(big_words, key=lambda x: x[2], reverse=reverse_order)
    return big_words


#TODO: Nouns might also need to be inflected. I'll look into it.
def modify_words(text, decreasing=True, score_data=None, target=None):
    """
    Chagnes the number of syllables in a text.
    Args:
        text (string): The text of a document
        decreasing (bool, optional): Decreasing order reduces syllables, increasing order increases syllables. Defaults to True
        score_data (dict, optional): A dictionary containing score data. See above method. Defaults to None.
        target (float, optional): A target flesch reading score to hit. Defaults to None.
    returns:
        text (string): Modified text with obfuscation
    """
    flesch_score = None
    s_words = sort_words(text, decreasing)
    for word, pos, syl_count, tok_tag in s_words:
        if pos not in SPACY_TAGS:
            continue
        syns = get_synonyms(word, pos)
        transforms = [(w, get_syllables(w)) for w in syns]
        for word_sub, syl_num in transforms:
            word_sub = word_sub.replace('_', ' ')
            # this section changes the tense of a verb i.e. exagerate -> exagerated
            if pos[0] == 'V':
                doc = nlp(word_sub)
                word_sub = doc[0]._.inflect(tok_tag)
            if decreasing:
                if syl_num < syl_count:
                    print('Replacement: {} ({}) -> {}'.format(word, pos[0], word_sub))
                    text = text.replace(word, word_sub, 1)
                    if score_data:
                        score_data['num_syllables'] -= (syl_count - syl_num)
                        flesch_score = calculate_score(score_data)
                        print('NEW SCORE:', flesch_score)
                    break
            else:
                 if syl_num > syl_count:
                    print('Replacement: {} ({}) -> {}'.format(word, pos[0], word_sub))
                    text = text.replace(word, word_sub, 1)
                    if score_data:
                        score_data['num_syllables'] += (syl_num - syl_count)
                        flesch_score = calculate_score(score_data)
                        print('NEW SCORE:', flesch_score)
                    break               

        if target and flesch_score:
            if decreasing and flesch_score > target:
                return text
            elif not decreasing and flesch_score < target:
                return text
    print(text)
    return text

# this method was supposed to reduce sentence length, but it's not really needed.
# def reduce_sentences(text, score_data=None, target=None):
    # doc = nlp(text)
    # for sent in doc.sents:
    #     if not sent:
    #         continue
        
    #     time.sleep(1)

def get_synonyms(word, pos):
    """Gets the synonym for a word.

    Args:
        word (string): The word to get a synonym for
        pos (string): The part of speech of the given word

    Returns:
        list[synset]: Returns a list of wordnet synsets for a given word.
    """
    return synonyms.get_synonyms(word, pos) 

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


def get_score_data(text):
    """Gets the score data in order to calculate the flesch reading score

    Args:
        text (str): A document

    Returns:
        dict: A dictionary containing score information
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
    score_data = {
        'num_words': num_words,
        'num_syllables': num_syllables,
        'num_sentences': num_sentences
    }
    return score_data 

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
    return TTR

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please specify a file.')
        sys.exit()
    filename = sys.argv[1]
    text = read_file(filename)
    score_data = get_score_data(text)
    if score_data < 70:
        modify_words(text, True, score_data, 70)
    else:
        modify_words(text, False, score_data, 70)


