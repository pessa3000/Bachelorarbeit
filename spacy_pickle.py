import pickle
import spacy
import os
import spacy_conll

nlp = spacy.load("ca_core_news_sm")
#nlp.add_pipe("conll_formatter", config={"include_headers": True}, last=True)
#doc = nlp("Hola Giacomo, com estàs?")

def pickle_write(doc, filename):
    folder= "pickles"
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, filename), "wb") as f:
        pickle.dump(doc, f)

def pickle_read(filename):
    folder= "pickles"
    with open(os.path.join(folder, filename), "rb") as f:
        data_loaded = pickle.load(f)
    return data_loaded


#with open("spacy_pickle.pickle", "rb") as f:
#    data_loaded = pickle.load(f)

#for token in doc:
#    print(token.text, token.dep_, token.pos_)

#print("*"*16)
#for token in data_loaded:
#    print(token.text, token.pos_, token.dep_, token.lemma_, token.head.dep_, token.morph)