import nltk
from nltk.tag import pos_tag
import re
import spacy
nlp = spacy.load('en_core_web_sm')


def sentSegs(taggedSent, grammar, loops = 1):     # sentenceParts; grammar = "NP: {<DT>?<JJ>*<NN>}"
    #if loops == "":
    #    loops = "loop=1"
    cp = nltk.RegexpParser(grammar, loops)
    result = cp.parse(taggedSent)
    return result

grammar = r"""
    NP:
        {<.*>+}
        }<IN|CC>+{
"""   

grammar = r"""                                                              # Mary saw the cat sit on the mat will yield
  NP: {<DT|JJ|PRP|NN.*>+}          # Chunk sequences of DT, JJ, NN                (S
  PP: {<IN><NP><>}              # Chunk prepositions followed by NP              (NP Mary/NN)
  VP: {<MD>?<RB.*>?<VB.*><RB.*>?<NP|PP|RP|CLAUSE>+} # Chunk verbs and their arguments                saw/VBD
  CLAUSE: {<NP><VP>+}           # Chunk NP, VP                                   (CLAUSE
""" 

OWL_dependent_markers = set(["after", "although", "as", "as if", "because", "before", "even if", "even though", "if", "in order to", "since", "though", "unless", "until", "whatever", "when", "whenever", "whether", "while"])


def clauseswitch(inputtext):
    punct = inputtext[-1]
    inputtext_nopunct = inputtext[:-1]
    sentenceParts = pos_tag(inputtext_nopunct.split()) 

    out = sentSegs(sentenceParts, grammar, 2)
    new_str = []
    clause_found = False
    clause_at = -1
    for enum, item in enumerate(out):
        if type(item) == nltk.Tree:
            if clause_found:
                for leaf in item.leaves():
                    new_str.append(leaf[0])
            else:
                pass
        
        elif type(item) == tuple:
            if item[0] in OWL_dependent_markers and not clause_found:
                if (len(out) > enum + 1) and type(out[enum + 1]) == nltk.Tree and out[enum + 1].label() == "CLAUSE":
                    clause_found = True
                    clause_at = enum
                    new_str.append(item[0])
            
            elif clause_found:
                new_str.append(item[0])

    if clause_found:
        new_str.append(",")
        flag = False
        for i in range(clause_at):
            if type(out[i]) == nltk.Tree:
                for leaf in out[i].leaves():
                    if not flag:
                        flag = True
                        new_str.append(leaf[0].lower())
                    else:
                        new_str.append(leaf[0])

            elif type(out[i]) == tuple:  
                new_str.append(out[i][0]) 
        

        new_str[0] = new_str[0].capitalize() 
        new_str.append(punct)

        return " ".join(new_str)


    else:
        return inputtext
    







from urllib import request
from nltk.tokenize import word_tokenize, sent_tokenize

def GetRawText(url):
    response = request.urlopen(url)
    raw = response.read().decode('utf8', "ignore")
    #remove non book stuff
    start_index = raw.find("***")
    end_of_line = raw.find("\n", start_index)
    return raw[end_of_line : ]



if __name__ == "__main__":
    print(clauseswitch("He was happy when it was saturday."))

    rawtxt = GetRawText("https://www.gutenberg.org/files/98/98-0.txt")
    
    tokens = sent_tokenize(rawtxt)


    tot_num_tok = len(tokens)
    num_transformed = 0

    print(len(tokens))
    


    for i, token in enumerate(tokens):
        
        sent_after_transform = clauseswitch(token)
        if sent_after_transform != token:

            # print("\n\n-----------------------------------")
            # print(token)
            # print(sent_after_transform)

            num_transformed += 1

        if i % 1000 == 0:
            print(i)

    print("num_transformed / total_tokens = {} / {}".format( num_transformed, tot_num_tok))