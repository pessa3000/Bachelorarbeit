#programa per analitzar arxius conllu de maneres diverses, anar provant :)
from conllu import parse
import os
#with open("prova_conll.conllu", "r") as f:
#    sentences = f.read()
#    conllu_parse = parse(sentences)

#de moment volem trobar la combinacio nom+adj

llista= [["upos", "DET"],["upos", "NOUN"]]

def file_to_conllu(filename):
    folder = "analysis"
    with open(os.path.join(folder, filename), "r") as f:
        sentences = f.read()
        return parse(sentences)
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
#receives a token and a dictionary of conditions to check on a single word(!)
def check_conds(sent, token, index, conds):
    #print("ey", type(conds))
    if not isinstance(conds, dict):
        print("error this is not a dict", conds, type(conds))
        return 1
    #all_met = all(token.get(k) == v for k, v in conds.items()) #this will have to become complicated
    for k, v in conds.items():
        #if it is a normal condition, check if it is false
        if isinstance(v, str) and isinstance(k, str):
            if token.get(k) != v:
                return False
            else:
                pass
        elif isinstance(k, str):  # else v is a function that will be applied, if it is not true, then stop
            if not v(sent, token, index, k):
                return False
            else:
                pass
        else:
            #print("we re going into unknown territory")
            if not k(sent, token, index, v):
                return False
            else:
                pass
    #print("flag :D")
    return token

#to be implemented z.B. like {parent_is: {"upos":"DET"}}
def parent_is(sent, token, index, conds):
    parent= sent[token.get("head")-1]
    if check_conds(sent, parent, token.get("head"), conds):
        print(sent)
        print("token", token, token.get("id"), token.get("head"))
        print("parent", parent, parent.get("id"))
        return True
    else:
        return False


#ex. {"head" : prev}
#example: rel-condition prev requires the key of the condition to be the same as the previous one
#k is the key of the cond

def prev_head(sent, token, index, k):
    if index == 1:
        return False
    if token.get(k) == index-1:
        return True
    else:
        #print(f'actual head of the token {token.get(k)}, prev token{index-1}')
        return False
def next_head(sent, token, index, k):
    if index == len(sent)-1:
        print(token)
        print("*************oops last word")
        return False
    elif token.get(k) == index+2:
        #print("true:_)")
        #print(token.get(k), sent[index-1],sent[index], sent[index+1])
        return True
    else:
        #print(token.get(k), index+1, type(token.get(k)), type(index+1))
        return False

#I want to check that, there are no other tokens that go to token with a certain deprel relation (to check for subjectless or objectless verbs, f.e)
def no_deprel(sent, token, index, k, dep="nsubj"):
    for token2 in sent:
        if token2.get("deprel") == dep and token2.get("head") == index+1:
            #print(f'{token2["form"]} is {dep} of {token["form"]}')
            #print(token)
            #print(token2)
            return False
    #print(f'{token["form"]} has no dependent with the relation {dep}')
    #print(f'feats {token["feats"]}')
    return True



#checks the whole corpus for single tokens which fullfill a dict of conditions, and counts them
def counter_conds(conllu_parse, conds):
    print("counter_conds being used")
    i=0
    if conds is not dict:
        print("error, this is not a dict")
        return 0
    for sent in conllu_parse:
        for token in sent:
            if check_conds(sent, token, index, conds):
                i=i+1
                print(check_conds(sent, token, conds)["form"])
                #print(sent)
    return i

def llargada_mitjana(filename):
    l=0
    if filename.endswith(".conllu"):
        conllu_parse = file_to_conllu(filename)
        for sent in conllu_parse:
            #print(len(sent))
            #print(sent.metadata["text"])
            l=l+len(sent)
        return l/len(conllu_parse)
    if filename.endswith(".txt"):
        print("we havent implemented this yet")
        return 1
        #folder = "sentences"
        #with open(os.path.join(folder, filename), "r") as f:
        #    sentences = f.read()
        #    return parse(sentences)

#so far conditions should be a list of dictionaries
#and it works btw :D
def check_conllu_for_conditions(filename, conditions, printf=False):
    conllu_parse= file_to_conllu(filename)
    l= len(conditions)
    llista =[]
    count=0 #counts how many times the conditions are fulfilled in the whole corpus
    if not isinstance(conditions, list):
        for conds in conditions:
            if not isinstance(conds, dict):
                print("error this is not a list of dicts")
                print(f'{conds} is a {type(conds)}')
    #print(f'dict of conds has {l} conditions')
    for sent in conllu_parse:

        #print(sent, "length", len(sent))
        n = len(sent)
        if n<l:
            #print("sentence too short to check conds")

            break
        else:
            #print(f'{l} conditions, {n} len(sent)')
            for j, token in enumerate(sent):
                if j >= n-l:
                    #print(f'{j} position erreicht, word {token}, break loop')
                    break
                else:
                    for i, cond in enumerate(conditions):
                        #print("checking cond", i, cond, "on token", sent[j+i])
                        #each cond is a dictionary of conditions to check on one word
                        if check_conds(sent, sent[j+i], j, cond):
                            #print(f'***condition {cond} met, token {sent[j+i]}')
                            if i == len(conditions)-1:
                                llista.append(token)
                                count+=1
                                if printf:
                                    print(f'\n match in sentence {sent.metadata["sent_id"]}')
                                    print(sent.metadata["text"])
                                for k in range(l):
                                    if printf:
                                     print(f'{sent[j+k]} fulfills {conditions[k]}')
                                     print(f'{sent[j+k]} h:{sent[j+k].get("head")} {sent[j+k+1].get("id")}')
                                     print(sent[j+k])
                                    pass
                        else:
                            break
            #print("i am using counter conds rn")
            #count= counter_conds(conllu_parse, conditions)

    #return llista
    return count

def check_conllu_for_conditions2(filename, conditions, printf=False):
    conllu_parse= file_to_conllu(filename)
    llista =[]
    count=0 #counts how many times the conditions are fulfilled in the whole corpus
    if not isinstance(conditions, list):
        for conds in conditions:
            if not isinstance(conds, dict):
                print("error this is not a list of dicts")
                print(f'{conds} is a {type(conds)}')
    #print(f'dict of conds has {l} conditions')
    for sent in conllu_parse:
        count= count + check_sent_for_conditions(sent, conditions, printf)
    #return llista
    return count

def check_sent_for_conditions(sent, conditions, printf=False):
    #print(sent, "length", len(sent))
    # add converting a text sent to a conllu parsed sent
    n = len(sent)
    l = len(conditions)
    counter=0
    #remove this condition, it is also tested as part of the for loop:
    #print(f'{l} conditions, {n} len(sent)')
    for j, token in enumerate(sent):
        if j >= n-l:
            return counter
        else:
            for i, cond in enumerate(conditions):
                #print("checking cond", i, cond, "on token", sent[j+i])
                #conditions is a list of dictionaries of conditions to check on consecutive words
                #each cond is a dictionary of conditions to check on one word
                if check_conds(sent, sent[j+i], j, cond):
                    #print(f'***condition {cond} met, token {sent[j+i]}')
                    if i == len(conditions)-1:
                        llista.append(token)
                        counter+=1
                        if printf:
                            print(f'\n match in sentence {sent.metadata["sent_id"]}')
                            print(sent.metadata["text"])
                        for k in range(l):
                            if printf:
                             print(f'{sent[j+k]} fulfills {conditions[k]}')
                             print(f'{sent[j+k]} h:{sent[j+k].get("head")} {sent[j+k+1].get("id")}')
                             print(sent[j+k])
                            pass
                else:
                    break
    #print("i am using counter conds rn")
        #count= counter_conds(conllu_parse, conditions)
    #return llista
    return counter



# def parent_is(conds=[{"upos": "VERB"}]):
#     for token2 in sent:
#         if token2.get("head") == index+1:
#             return check_conds(token2, token, index, conds)
#         else:
#             return False



#print(check_conllu_for_conditions("tv3_incendis.conllu", [ { "misc": parent_is("NOUN")} ] ) )


#exemples llistes
llista_conds= [{"upos":"DET", "form":"un"}, {"deprel": "nsubj", "upos": "NOUN"}]
#trobar frases en que el subjecte es un nom, pronom o saber si no esta realitzat

#llista_conds_subj= [{"deprel": "nsubj", "upos": "NOUN"}, {"deprel": "nsubj", "upos": "PROPN"}, {"deprel": "nsubj", "upos": "PRON"}]

conds_article = [{"upos":"DET"}]
conds_det_nom_subj = [{"upos": "DET" },{"upos": "NOUN", "deprel": "obj"}]

conds_adj_nom = [{"upos": "ADJ", "head": next_head}, {"upos": "NOUN"}]
conds_nom_adj = [{"upos": "NOUN"}, {"upos": "ADJ", "head": prev_head}]

conds_nom_subj = [{"upos": "NOUN", "deprel": "nsubj"}]
conds_pron_subj = [{"upos": "PRON", "deprel": "nsubj"}]
conds_propn_subj = [{"upos": "PROPN", "deprel": "nsubj"}]
conds_no_subj = [{"upos": "VERB", "deprel": no_deprel}]
conds_parent_noun = [{parent_is: {"upos": "NOUN"}}]
#print(check_conllu_for_conditions("200_ca_spacy_low.conllu", conds_det_nom_subj))
print(check_conllu_for_conditions2("tv3_incendis.conllu", conds_parent_noun))
#print(check_conllu_for_conditions("tv3_corrupcio.conllu", conds_nom_subj))
#print(check_conllu_for_conditions("tv3_incendis.conllu", [{"upos": "ADJ", "head": next_head}, {"upos": "NOUN"}], printf=True))
#print(check_conllu_for_conditions("KI_incendis.conllu", conds_adj_nom, printf=True))

file_list= ["tv3_incendis.conllu", "KI_incendis.conllu"]
conditions_list= [conds_adj_nom, conds_nom_adj, conds_nom_subj, conds_propn_subj]

# print(f'total verbs {check_conllu_for_conditions("tv3_incendis.conllu", [{"upos": "VERB"}])}')
# print(f'Verbs with no explicit subj: {check_conllu_for_conditions("tv3_incendis.conllu", conds_no_subj)}')
# print(f'nsubjs prop noun as subject {check_conllu_for_conditions("tv3_incendis.conllu", conds_propn_subj)}')
# print(f'nsubjs with a noun as subj {check_conllu_for_conditions("tv3_incendis.conllu", conds_nom_subj)}')
# print(f'nsubjs with a noun as subj {check_conllu_for_conditions("tv3_incendis.conllu", conds_pron_subj)}')
# print(f'nsubjs {check_conllu_for_conditions("tv3_incendis.conllu", [{"deprel": "nsubj"}])}')

#for condition in conditions_list:
#    for file in file_list:
#        print(file, 100*check_conllu_for_conditions(file, condition, printf=False)/len(file_to_conllu(file)), condition)

set = set()
for sent in file_to_conllu("tv3_incendis.conllu"):
    for token in sent:
        if token["deprel"] == "nsubj":
            set.add(token["upos"])

print(set)