#programa per analitzar arxius conllu de maneres diverses, anar provant :)
from conllu import parse

with open("prova_conll.conllu", "r") as f:
    sentences = f.read()
    conllu_parse = parse(sentences)

#de moment volem trobar la combinacio nom+adj

llista= [["upos", "DET"],["upos", "NOUN"]]

#nomes funciona amb llistes de 2 tipus
#aquesta funcio no esta actualitzada pq encara no rep dicctionaris de condicions
def trobar_combinacio(sentences, llista):
    for sent in sentences:
        #print(sent)
        for index, token in enumerate(sent):
            if token[llista[1][0]] == llista[1][1]:
                if index >=1:
                    #print(index, token["upos"])
                    prev_el= sent[int(index)-1]
                    #print(prev_el["form"], prev_el["upos"])
                    if prev_el[llista[0][0]] == llista[0][1]:
                        print(f'{llista[0][1]} + {llista[1][1]} {prev_el["form"]} {token["form"]}')

#trobar_combinacio(conllu_parse, llista)
#receives a token and a dictionary of conditions to check on the same word
def check_conds(token, conds):
    all_met = all(token.get(k) == v for k, v in conds.items())
    if all_met:
        #print(f'match {token["form"]}')
        return token
    else:
        return 0

#checks the whole corpus for single tokens which fullfill a dict of conditions, and counts them
def counter_conds(conllu_parse, conds):
    i=0
    for sent in conllu_parse:
        for token in sent:
            if check_conds(token, conds):
                i=i+1
                print(check_conds(token, conds)["form"])
                #print(sent)
    return i
#needs improvement: checks conditions on 2 consequetive words
def condicions_consec(sent, cond):
    for index, token in enumerate(sent):
        print(sent)
        print(index, token)
        for key, value in cond[0].items():
            print(key, value)
            if token[value] == cond[0][value]:
                print(f'match! {token[value]}, {cond[0][value]}\n')
            else:
                print(f'no match! {token[value]}, {cond[0][value]}\n')

llista_conds= [{"upos":"DET", "form":"un"}, {"deprel": "nsubj", "upos": "NOUN"}]
#trobar frases en que el subjecte es un nom, pronom o saber si no esta realitzat

llista_conds_subj= [{"deprel": "nsubj", "upos": "NOUN"}, {"deprel": "nsubj", "upos": "PROPN"}, {"deprel": "nsubj", "upos": "PRON"}]

conds_article = [{"upos":"DET"}]
for index, cond in enumerate(conds_article):
    print(f'numero de cops q es compleix cond {index}: {counter_conds(conllu_parse, cond)} \n')


# for sent in conllu_parse:
#     print(sent, "\n")
#
#     for token in sent:
#         print(token["id"], token["form"], token["lemma"], token["upos"], token["deprel"])
