"""
THIS MAY NOT WORK PROPERLY IF YOU DON'T HAVE THE RIGHT CHROMEDRIVER FOR YOUR COMPUTER.
https://chromedriver.chromium.org/downloads
"""
url = 'https://www.thesaurus.com/browse/'

from selenium import webdriver
import time

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
        print(synonym.text)
        syns.append(synonym.text)
    return syns

def get_synonyms(word, pos):
    """Gets the synonyms from thesaurus.com

    Args:
        word (str): The word to replace
        pos (str): The part of speech of the word

    Returns:
        (list[str]): A list of synonyms
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=PATH, options=options)
    driver.get(url + word)
    header = driver.find_element_by_id('headword')
    tabsList = header.find_elements_by_tag_name('li')
    if len(tabsList) > 1:
        for i, tab in enumerate(tabsList):
            part_of_speech = tab.find_element_by_tag_name('em')
            pos_text = part_of_speech.get_attribute('innerHTML')
            print(pos_text)
            if pos_text == pos:
                link = tab.find_element_by_tag_name('a')
                print(link.get_attribute('innerHTML'))
                link.click()
                meanings = get_meanings(driver)
                driver.quit()
                return meanings
    meanings = get_meanings(driver)
    driver.quit()
    return meanings 
    