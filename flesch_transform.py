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


FANBOYS = ['for', 'and', 'nor', 'but', 'or', 'yet', 'so']


class Flesch:

    def __init__(self, text, ideal=70, score_data=None):
        self.text = text
        self.ideal = ideal
        self.score_data = score_data if score_data else self.get_score(text)
        self.SPACY_TAGS = ['ADJ', 'ADV', 'NOUN', 'VERB']
        self.SCORE_CONSTANT = 206.835

    def calculate_score(self, score_data):
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
        return self.SCORE_CONSTANT - (1.015 * asl) - (84.6 * asw)

    def sort_words(self, reverse_order=True):
        """Parses and sorts words in a document

        Args:
            text (str): A document
            reverse_order (bool, optional): This will order the words from the most syllables to the least. Defaults to True.

        Returns:

            (word, Part of Speech, # Syllables, spacy tag): A tuple containing a bunch of information about a word
        """
        doc = nlp(self.text)
        no_stopwords = []
        for token in doc:
            if token.text not in stopwords.words():
                # Special case for verbs, get the tense
                no_stopwords.append((token.text, token.pos_, token.tag_))
        big_words = []
        for word, pos, tok_tag in no_stopwords:
            if re.search(r'([\w\-\s]+)\w+', word):
                big_words.append((word, pos, self.get_syllables(word), tok_tag))
        big_words = sorted(big_words, key=lambda x: x[2], reverse=reverse_order)
        return big_words

    def get_score(self, text):
        """Gets the score data in order to calculate the flesch reading score

        Args:
            text (str): A document

        Returns:
            dict: A dictionary containing score information
        """
        self.SCORE_CONSTANT = 206.835
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
                    num_syllables += self.get_syllables(word)
        score_data = {
            'num_words': num_words,
            'num_syllables': num_syllables,
            'num_sentences': num_sentences
        }
        return score_data 

    def get_syllables(self, word):
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

    def get_synonyms(self, word, pos):
        """Gets the synonym for a word.

        Args:
            word (string): The word to get a synonym for
            pos (string): The part of speech of the given word

        Returns:
            list[synset]: Returns a list of wordnet synsets for a given word.
        """
        return synonyms.get_synonyms(word, pos) 

    def transform(self, decreasing=True, target=None, max_transforms = None):

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

        # initializing values
        score_data = self.score_data if self.score_data else None
        if score_data:
            flesch_score = self.calculate_score(score_data)
            if (abs(flesch_score - target) > 10):
                if flesch_score - target > 0:
                    decreasing = False
                else:
                    decreasing = True
            else:
                target += 10
                if flesch_score - target > 0:
                    decreasing = False
                else:
                    decreasing = True
        else:
            decreasing = True
            flesch_score = None

        text = self.text
        s_words = self.sort_words(decreasing)
        transform_count = 0
        for word, pos, syl_count, tok_tag in s_words:
            transform_count += 1
            if max_transforms and transform_count > max_transforms:
                break 
            if pos not in self.SPACY_TAGS:
                continue
            syns = self.get_synonyms(word, pos)
            if not syns:
                continue
            transforms = [(w, self.get_syllables(w)) for w in syns]
            for word_sub, syl_num in transforms:
                word_sub = word_sub.replace('_', ' ')
                # this section changes the tense of a verb i.e. exagerate -> exagerated or the inflection of a noun i.e. dog -> dogs
                if pos[0] == 'V' or pos[0] == 'N':
                    doc = nlp(word_sub)
                    word_sub = doc[0]._.inflect(tok_tag)
                if decreasing:
                    if syl_num < syl_count:
                        text = text.replace(word, word_sub, 1)
                        if score_data:
                            score_data['num_syllables'] -= (syl_count - syl_num)
                            flesch_score = self.calculate_score(score_data)
                else:
                    if syl_num > syl_count:
                        text = text.replace(word, word_sub, 1)
                        if score_data:
                            score_data['num_syllables'] += (syl_num - syl_count)
                            flesch_score = self.calculate_score(score_data)
                if target and flesch_score:
                    if decreasing and flesch_score > target:
                        return text
                    elif not decreasing and flesch_score < target:
                        return text
        return text

def get_synonyms(word, pos):
    """Gets the synonym for a word.

    Args:
        word (string): The word to get a synonym for
        pos (string): The part of speech of the given word

    Returns:
        list[synset]: Returns a list of wordnet synsets for a given word.
    """
    return synonyms.get_synonyms(word, pos) 

def get_score_data(text):
    """Gets the score data in order to calculate the flesch reading score

    Args:
        text (str): A document

    Returns:
        dict: A dictionary containing score information
    """
    self.SCORE_CONSTANT = 206.835
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
                num_syllables += self.get_syllables(word)
    score_data = {
        'num_words': num_words,
        'num_syllables': num_syllables,
        'num_sentences': num_sentences
    }
    return score_data 

def read_file(filepath):
    f = open(filepath, 'r', encoding="utf-8")
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
    flesch = Flesch(text)
    out = flesch.transform(target=70)
    # score_data = get_score_data(text)
    # if score_data < 70:
    #     modify_words(text, True, score_data, 70)
    # else:
    #     modify_words(text, False, score_data, 70)


