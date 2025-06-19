from pyconll import load_from_file
from spacy_conllu import clean_text

import os
#arxiu amb eines per comparar anotacions fetes en un arxiu en format conllu :)

# this code takes the first n sentences from a conllu file and prints their text to a file :D
# deanotating texts
def deanotate(filename, num):
    folder = "deanotate"
    os.makedirs(os.path.join(folder, filename), exist_ok=True)
    data = load_from_file(filename)
    carro = ""
    for index, sentence in enumerate(data):
        if index < num:
            #sentence.id = index+1
            carro = carro + str(sentence.text) + "\n\n"
        else:
            #carro = carro + "\n"
            break
    carro = carro + "\n"

    with open("deanotate/d"+ str(num) + "_" + filename +".txt", "w") as f:
        f.write(carro)

#deanotate("ca_ancora-ud-train.conllu", 50)

def count_alpha_tokens(data):
    count = 0
    countj =0
    for sentence in data:
        for token in sentence:
            countj += 1
            if token.form.isalpha():
               count += 1
            else:
                pass
                #print(token.form)
    #print(f"number of alpha tokens: {count}")
    #print(f"number of total tokens: {countj}")
    return count
#deanotate("ca_ancora-ud-train.conllu", 50)
frases_eliminades=[5,22, 28]
# el motiu per eliminar les es que no tneen el mateix numero de tokens, ja que hi ha alguna contraccio en un connector (ex. "Pel que fa")




#funcio per comparar les dues anotacions de conllu del mateix text
"""
List of attributes of tokens that can be compared:
['AV_DEPS_SEPARATOR', 'AV_SEPARATOR', 'BY_CASE_INSENSITIVE', 'BY_ID', 'COMPONENT_DELIMITER', 'EMPTY', 'FIELD_DELIMITER', 'V_DELIMITER', 'V_DEPS_DELIMITER', '__abstractmethods__', '__annotations__', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '__weakref__', '_abc_impl',
'_form', 'conll', 'deprel', 'deps', 'feats', 'form', 'head', 'id', 'is_empty_node', 'is_multiword', 'lemma', 'misc', 'upos', 'xpos']
"""
def test_annotation(annotation1, annotation2, num, attribute="upos", printf=0):
    count = 0
    data1 = load_from_file(annotation1)
    data2 = load_from_file(annotation2)
    for index, (sentence1, sentence2) in enumerate(zip(data1, data2)):
        print(index)
        if index in frases_eliminades:
            #print(index, "was skipped")
            continue
        if index < num:
            if clean_text(sentence1.text).lower() != clean_text(sentence2.text).lower():
                print ("error, not the same text")
                print(clean_text(sentence2.text))
                print (sentence1.text + "\n" + sentence2.text )
                return 1
            #print(sentence1.text)
            #word_pairs= [x for x in zip(sentence1, sentence2) if x[1].is_multiword()==False and x[0].is_multiword()== False]
            #generating the word pairs for each sentence!!!
        word_pairs=[]
        j = 0
        k =0
        for i in range(min(len(sentence1), len(sentence2))):
            if sentence1[i].is_multiword() ==True or sentence1[i].form.lower == "'Pel'":
                j+=1
            if sentence2[i].is_multiword()==True:
                k+=1
            word_pairs.append( (sentence1[i+j], sentence2[i+k]) )
            print((sentence1[i+j].form, sentence2[i+k].form), "j=", j, "k=", k)

        for token1, token2 in word_pairs:
            if token1.is_multiword()==True:
                continue
            elif type(getattr(token2, attribute)) != str:
                if getattr(token2, attribute) != getattr(token1, attribute):
                    count+=1
                    if printf:
                        #print("WARNING this is not a string", attribute, token1.form, getattr(token1, attribute))
                        print(sentence1.text)
                        print(token1.form, token2.form)
                        print("token1:", getattr(token1, attribute),"token2:",getattr(token2, attribute), "\n")
                continue
            elif clean_text(token1.form) != clean_text(token2.form):
                pass
                #print("error, not the same text, tokens dont match")
                #print(clean_text(token1.form), clean_text(token2.form))
                #return 1
            elif getattr(token1, attribute) ==None:
                print("WARNING", attribute, token1.form, token1.upos)
            elif getattr(token1, attribute).lower() != getattr(token2, attribute).lower():
                if token1.form.isalpha()==True:
                    if printf == True:
                        print(sentence1.text)
                        print(token1.form, token2.form)
                        print(getattr(token1, attribute), getattr(token2, attribute), "\n")
                    count+=1
                #print("*" *16)
                pass
            else:
                pass
        #print(sentence1.text)
            # for pair in word_pairs:
            #     print(pair[0].form, pair[1].form)
            #     print(pair[0].upos, pair[1].upos)
            #     print(getattr(pair[0], "upos"), getattr(pair[1], "upos"))
    return 100*count/count_alpha_tokens(data1)

llista_attributs=['deprel', 'feats', 'form', 'head', 'id', 'lemma', 'upos']
# altres_atributs= ['misc',  'deps'] #donen problemes pq no te gaire sentit comparar-los
# for attribute in llista_attributs:
#     #print(attribute, test_annotation("50_ca_ancora-ud-train.conllu.txt", "50_spacy_ancora.conllu", 50, attribute, printf= 0))
#     print(attribute, test_annotation("50_ca_ancora-ud-train.conllu.txt", "50_ca_spacy.conllu", 50, attribute, printf= 0))
    #print(attribute, test_annotation("50_ca_ancora-ud-train.conllu.txt", "50_spacy_ancora.conllu", 50, attribute, 0))

data= load_from_file("50_ca_spacy.conllu")

# for sentence in data:
#     print(sentence.text, "*"*16)

#test_annotation("50_ca_ancora-ud-train.conllu.txt", "50_spacy_ancora.conllu", 50, "upos", printf= 1)
test_annotation("50_ca_ancora-ud-train.conllu.txt", "50_ca_spacy.conllu", 50, "upos", printf= 1)