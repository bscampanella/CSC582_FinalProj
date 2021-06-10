from nltk.corpus import wordnet as wn
import spacy
nlp = spacy.load("en_core_web_sm")


def change_sent_not(testsent):
    pron = ""
    fin_text = testsent
    negative_replace = ""
    doc = nlp(testsent)
    for i, token in enumerate(doc):
        if token.pos_ == "PRON":
            pron = token.text

        if token.lemma_ == "be":
            cur_text = ""
            
            if (len(doc) > i+1) and  (doc[i + 1].pos_ == "ADJ") :
                cur_text = doc[i + 1].text
            elif (len(doc) > i+2) and (doc[i + 1].pos_ == "ADV" and doc[i + 2].pos_ == "ADJ"):
                cur_text = doc[i + 2].text
            if cur_text != "":
                cur_synset = None
                if len(wn.synsets(cur_text, pos="a")):
                    cur_synset = wn.synsets(cur_text, pos='a')[0]
                elif len(wn.synsets(cur_text, pos="s")):
                    cur_synset = wn.synsets(cur_text, pos='s')[0]
                elif len( wn.synsets(cur_text)):
                    cur_synset = wn.synsets(cur_text)[0]


                if cur_synset:
                    if (len(cur_synset.hypernyms()) and len(cur_synset.hypernyms()[0].hyponyms())):
                        for hypo in cur_synset.hypernyms()[0].hyponyms():
                            if hypo.lemmas()[0].name() != cur_text:
                                negative_replace = hypo.lemmas()[0].name()
                                break
                    elif len(cur_synset.lemmas()):
                        if len(cur_synset.lemmas()[0].antonyms()):
                            negative_replace = cur_synset.lemmas()[0].antonyms()[0].name()
                        else:
                            for lm in cur_synset.lemmas():
                                if lm.name() != cur_text:
                                    negative_replace = lm.name()

            if negative_replace != "":
                fin_text = ""
                for x in range(i + 1):
                    fin_text += doc[x].text + " "
                
                fin_text += "not " + negative_replace 
                #here use the spacy ner to see if a person is in sentence and if so
                # them change it to they
                doc2 = nlp(fin_text)
                ents_lst = []
                for ent in doc2.ents:
                    ents_lst.append(ent.text)

                replace_tok = ""
                if pron:
                    replace_tok = pron
                elif ents_lst:
                    replace_tok = ents_lst[0]
                else:
                    replace_tok = "it"


                fin_text += ", " + replace_tok + " " + doc[i].text + " "
                for x in range(i + 1, len(doc)):
                    fin_text += doc[x].text + " "
    return fin_text


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
    print(change_sent_not("He is happy about his car."))

    rawtxt = GetRawText("https://www.gutenberg.org/files/98/98-0.txt")
    
    tokens = sent_tokenize(rawtxt)


    tot_num_tok = len(tokens)
    num_transformed = 0

    print(len(tokens))
    

    for i, token in enumerate(tokens):
        
        sent_after_transform = change_sent_not(token)
        if sent_after_transform != token:
            # print(token)
            # print(sent_after_transform)
            num_transformed += 1

        if i % 1000 == 0:
            print(i)


    print("num_transformed / total_tokens = {} / {}".format( num_transformed, tot_num_tok))