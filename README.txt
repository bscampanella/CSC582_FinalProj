
Written by Alex Rodgers and Brandon Campanella
Advised by Dr. Foaad Khosmood
For completion of CSC 582 Final Project while at Cal Poly San Luis Obispo
Style Obfuscation using Language Transformations

Coded in python
requirements.txt contains all of the necessary libraries in order to run this Project
Notably author_classifier.ipynb is the file to run to produce most of the results found in the assiciated paper

------Data--------
Note data is downloaded at runtime inside author_classifier.ipynb!!!
It is a fast process and should not take longer than a minute or two



Breif Discripton of Files
--------------------------------------------

author_classifier.ipynb                      -- Main notebook that downloads the gutenberg data, extracts features, trains classifier and runs tests on transforms
bi_vocab.txt                                 -- for use in ngram feature extracter
bookdata.json                                -- pre-extracted features for use if extracting features takes too long
chromedriver.exe                             -- for use with flesch transform
clauseswitch_transform.py                    -- function definition for the clause switcher transform
dale-chall.pkl                               -- 
Dependent_independent_clauseswitch.ipynb     -- develoment area for clause switcher
download.sh                                  --
flesch_transform.py                          -- function definition for flesch transform
gather_wordfreq.py                           --
get_gutenburg.ipynb                          -- development area for gutenberg corpus download
not_adj_test.ipynb                           -- function definition for not to be, to be transform
not_adj_transform.py                         -- devloment area for not to be transform
Pipfile                                      -- for use with pip environment handler
Pipfile.lock                                 -- for use with pip environment handler     
potter.txt                                   -- text data from harry potter for example purposes    
README.txt                                   -- this file    
requirements.txt                             -- requirements to run         
synonyms.py                                  -- develoment file    
tfidf.ipynb                                  -- develoment file for tfidf transfrom    
tfidf.txt                                    -- helper filer for tfidf  
tfidf_freq.txt                               -- helper file from tfidf       
uni_vocab.txt                                -- for use with unigram feature extractor   
word_freq.txt                                -- for use with tfidf transform      
word_occurence.txt                           -- helper file for tfidf 
zipf_transform.py                            -- now invalidated           