"""
THIS MAY NOT WORK PROPERLY IF YOU DON'T HAVE THE RIGHT CHROMEDRIVER FOR YOUR COMPUTER.
https://chromedriver.chromium.org/downloads
"""
url = 'https://www.thesaurus.com/browse/'

# from selenium import webdriver
import time
from nltk.corpus import wordnet as wn

# I'm using absolute path but maybe I can use local path.
PATH = './chromedriver'

def get_meanings(driver):
    """Gets the synonyms from thesaurus.com

    Args:
        driver ([type]): Selenium driver

    Returns:
        [list[str]]: Returns a list of synonyms
    """
    syns = []
    meanings = driver.find_element_by_id('meanings')
    synonym_list = meanings.find_element_by_tag_name('ul')
    synonyms = synonym_list.find_elements_by_tag_name('a')
    for synonym in synonyms:
        syns.append(synonym.text)
    return syns

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



def get_synonyms_manual(word, pos):
    syn = list()
    synsets = wn.synsets(word, pos=pos_to_wordnet_pos(pos))
    if not synsets:
        return []
    else:
       synset = synsets[0] 
    for lemma in synset.lemmas():
        syn.append(lemma.name())
    print(syn)
    return syn

def get_synonyms(word, pos, nltk=True):
    """Gets the synonyms from thesaurus.com

    Args:
        word (str): The word to replace
        pos (str): The part of speech of the word

    Returns:
        (list[str]): A list of synonyms
    """
    if nltk:
        return get_synonyms_manual(word, pos)
    # options = webdriver.ChromeOptions()
    # options.add_argument('--ignore-certificate-errors')
    # options.add_argument('--ignore-ssl-errors')
    # options.add_argument('--headless')
    # driver = webdriver.Chrome(executable_path=PATH, options=options)
    # driver.get(url + word)
    # header = driver.find_element_by_id('headword')
    # tabsList = header.find_elements_by_tag_name('li')
    # if len(tabsList) > 1:
    #     for i, tab in enumerate(tabsList):
    #         part_of_speech = tab.find_element_by_tag_name('em')
    #         pos_text = part_of_speech.get_attribute('innerHTML')
    #         if pos_text == pos:
    #             link = tab.find_element_by_tag_name('a')
    #             link.click()
    #             meanings = get_meanings(driver)
    #             driver.quit()
    #             return meanings
    # meanings = get_meanings(driver)
    # driver.quit()
    meanings = []
    return meanings 
    