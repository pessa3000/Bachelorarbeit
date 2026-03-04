#programa per analitzar arxius conllu de maneres diverses, anar provant :)
from conllu import parse
import os
from functools import wraps
import glob
import json
import datetime
#with open("prova_conll.conllu", "r") as f:
#    sentences = f.read()
#    conllu_parse = parse(sentences)



llista= [["upos", "DET"],["upos", "NOUN"]]

def file_to_conllu(filename):
    folder = "analysed_corpus"
    with open(os.path.join(folder, filename), "r") as f:
        sentences = f.read()
        return parse(sentences)

#receives a token and a dictionary of conditions to check on a single word(!)
def check_conds(sent, token, index, conds):
    #print("ey", type(conds))
    if not isinstance(conds, dict):
        print("error this is not a dict", conds, type(conds))
        raise TypeError(f"Only dicts are allowed, got {conds} instead, which is {type(conds)}")

    #all_met = all(token.get(k) == v for k, v in conds.items()) #this will have to become complicated
    for k, v in conds.items():
        #if it is a normal condition, check if it is false
        if isinstance(v, str) and isinstance(k, str):
            if token.get(k) != v:
                return False
            else:
                pass
            #when should even k be a dictionary??!
        elif isinstance(k, str) or isinstance(k, dict):  # else v is a function that will be applied, if it is not true, then stop
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
    #return token
    return True


############## ab hier gibt es meine selbsdefinierte funcitonen, um sahcen in dem corpus zu schauen


#USED TO NEGATE FUNCTIONS
def nicht(f):
    @wraps(f)
    def g(*args,**kwargs):
        return not f(*args,**kwargs)
    g.__name__ = f'negate({f.__name__})'
    return g



#Requires a dictionary of features to be checked :)
def feats_include(sent, token, index, feat_dict):
    if not isinstance(feat_dict, dict):
        print("error, feats_include requires a dictionary of feats")
        return False
    if not token.get("feats"):
        return False
    elif isinstance(token["feats"], dict):
        for keys, values in feat_dict.items():
            if keys not in token["feats"].keys():
                #print(keys, "missing")
                return False
            elif feat_dict[keys] != token["feats"][keys]:
                #print(keys, "value dont match", feat_dict[keys], "is not", token["feats"][keys])
                return False
        #print("\t OLEE", token["feats"])
        return True
    return True

#to be implemented z.B. like {parent_is: {"upos":"DET"}}
def parent_is(sent, token, index, conds):
    parent= sent[token.get("head")-1]
    if check_conds(sent, parent, token.get("head")-1, conds):
        #print(sent)
        #print("token", token, token.get("id"), token.get("head"))
        #print("parent", parent, parent.get("id"))
        return True
    else:
        return False
#TO BE IPMLEMENTED like this:
#{is_not: {"upos":"NOUN", "deprel": "nsubj"}}
# returns negative if the token fulfulls ALL conds (this is, in the example obj nouns reutrn trre)
def is_not(sent, token, index, conds):
    if check_conds(sent, token, index, conds):
        return False
    else:
        return True

#if any of the conditions in the list are fulfilled, it is negative
def is_not_any_of(sent, token, index, l_conds):
    for condy in l_conds:
        if check_conds(sent, token, index, condy):
            return False
    return True

#to be used like parent is: {has_son: {"deprel": "nsubj"}}
# it can't receive lists of conditions, it checks one single dict the son must fullfill ALL CONDITIONS
# it should not be used in a merge conditions setting
def has_son(sent, token, index, conds):
    for word in sent:
        if word.get("head") == token.get("id"):
            if check_conds(sent, word, word.get("id")-1, conds):
                #print("token", token.get("form"))
                #print("word", word, sent[word.get("head")-1].get("form"))
                #print(conds)
                return True
            else:
                pass
    return False

#same but l_conds is a list of what the different sons should fulfill:
# so there should be all of the sons there, the conditions in the list can be fulfilled by different sons
#example: has_sons: [{"deprel": "nsubj", feats_include: {"PronType": "Rel"} } ]
def has_sons(sent, token, index, l_conds):
    for i, condy in enumerate(l_conds):
        #print(f"\tchecking parents of {token} for cond. {i} of {len(l_conds)}")
        if not has_son(sent, token, index, condy):
            return False
        else:
            #print(f"\t\tcon {i} fulfilled")
            pass
    return True

# for condition dictionaries {x: y}
# where x is either str (i.e. "upos", or a function, i.e. "parent_is)
# where if x is a str, y can be another str (i.e. "NOUN" or another function i.e. no_weak_pronoun )
# if x is a function, it can be a dictionary (i.e. parent_is : {"upos":"noun"})
#                       or a list of dictionaries (i.e. has_sons: [c1, c2]
#                       or a string maybe?
def merge_conditions_dicts(d1, d2):
    z = {}
    # checking if conditions are repeated
    intersecting_keys = set(d1.keys()).intersection(set(d2.keys()))
    #print("intersecting keys:", intersecting_keys)
    for key in intersecting_keys:
        # case 0: value types not matching
        if type(d1[key]) != type(d2[key]):
            z[key] = f"err: value type for {key} not matching: {type(d1[key])} and {type(d2[key])}"
            return z
        # case 1: value is a string (x: "NOUN")
        elif type(d1[key]) is str:
            if d1[key] != d2[key]:
                print(f"\t*\tzero intersection:{key} conflict: {d1[key]} != {d2[key]}")
                z[key] = "impossible"
                return z
            else:
                z[key] = d1[key]
        #case 2: value is a dict (ex. {parent_is : {}}; or feats_include : {} )
        elif type(d1[key]) is dict:
            # print("attempting to merge nested dict")
            z[key] = merge_conditions_dicts(d1[key], d2[key])
        # case 3: value is a list
        # we just append lists and the function preceding them will decide what to do with them
        elif type(d1[key]) is list:
            z[key] = d1[key]+d2[key]
        else:
            print("we re trying to merge dicts and dont know what is going on", type(d1[key]))
    # regarding other keys, they will be just appended to z
    # print("adding non intersecting keys")
    for key in list(set(d1.keys()) -set(d1.keys()).intersection(set(d2.keys()))):
        z[key] = d1[key]
        #print(key, z[key])
    for key in set(d2.keys()) -set(d2.keys()).intersection(set(d1.keys())):
        z[key] = d2[key]
        #print(key, z[key])
    return z



# conditions are still lsits of one dictionary!
# It receives "evals":
# EX: l4 = {"l4": [c4]}, where c4 is a dictionary of conditions
def merge_evals(condict1, condict2):
    #print(f"merging:\n {condict1}\n and:\n {condict2}")
    #print("dict2", condict2, "\n")
    mega_dict= {}
    if not condict1 or not condict2:
        #print("error one of the evals is empty")
        #print(condict1, condict2)
        return 0
    for name1,cond1 in condict1.items():
        for name2, cond2 in condict2.items():
            #print(name1, cond1)
            #print(name2, cond2)
            condy1=cond1[0]
            condy2=cond2[0]
            z = merge_conditions_dicts(condy1, condy2)
            #making z a stupid list of dicts again sigh
            mega_dict.update({name1 + "__UND__" + name2 : [z]})
    #for cross_name, cross_cond in mega_dict.items():
        #print("RESULT:", cross_name, "::::", cross_cond, "\n")

    return mega_dict
#fa totes les interseccions possibles entre els elements d una llista d evals
def merge_list_evals(cond_list):
    if type(cond_list) is not list:
        print("error, merge_list_evals requires a list!")
        return 0
    else:
        a= cond_list[0]
        for item in cond_list:
            a = merge_evals(a, item)
        return a


# same workings as has_no_sons
# if there is a son that fullfills at least 1 cond, it is false ~(AuB)
def has_no_sons(sent, token, index, l_conds):
    for i, condy in enumerate(l_conds):
        #print(f"\tchecking parents of {token} for cond. {i} of {len(l_conds)}")
        if has_son(sent, token, index, condy):
            return False
        else:
            #print(f"\t\tcon {i} fulfilled")
            pass
    return True





#If there is a son that fullfills all the conds, it is false
# If there is none, it is true
def has_no_son(sent, token, index, conds):
    for word in sent:
        if word.get("head") == token.get("id"):
            if check_conds(sent, word, word.get("id")-1, conds):
                #print("token", token.get("form"))
                #print("word", word, sent[word.get("head")-1].get("form"))
                #print(conds)
                return False
            else:
                pass
    return True

# checks: head is the word right after / before the token
#ex. {"head": next_head}
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

# checks if the head comes before or after a word
def head_smaller_than_id(sent, token, index, k):
    if token.get(k) <= index+1:
        #print(token.get(k), ">=", index+1)
        if token.get(k) == index+1:
            print("wtf", token.get("form"), sent[index+1])
            print("ERROR: autohead detected, debugging time", token.get("form"), sent[index+1])
        return True
    else:
        return False

def head_greater_than_id(sent, token, index, k):
    if token.get(k) >= index+1:
        #print(token.get(k), ">=", index + 1)
        if token.get(k) == index+1:
            print("wtf", token.get("form"), sent[index+1])
            print("ERROR: autohead detected, debugging time", token.get("form"), sent[index + 1])
        return True
    else:
        return False

def no_weak_pronoun(sent, token, index, k):
    pron_list= {"hi", "en", "n’", "ne", "me", "te", "el", "la", "se", "nos", "vos", "li", "ho", "lo",  "s’", "els", "los", "ser"}
    if token.get('lemma') in pron_list and token.get("upos") == "PRON":
        return False
    else:
        #print(token, token.get('lemma'))
        return True

# wannacry
def obj_or_iobj(sent, token, index, k):
    deprel_list= {"iobj", "obj"}
    if token.get('deprel') in deprel_list:
        return True
    else:
        #print(token, token.get('lemma'))
        return False


# This is necessary to check that the arguments of a verb are NOT subordinate clauses
# in copulative subordinate clauses the token with the deprel is the head of the predicate
def is_sub_clause_head_core_arg(sent, token, index, k):
    clause_complement_deprels= ["csubj", "ccomp", "xcomp"]
    if token.get("deprel") in clause_complement_deprels:
                return True
    else:
        return False

def is_sub_clause_head(sent, token, index, k):
    clause_complement_deprels= ["csubj", "ccomp", "advcl", "acl", "xcomp"]
    if token.get("deprel") in clause_complement_deprels:
                return True
    else:
        return False

# condition on the object, such that, if there's subj, and SO, true
# idea: rewrite it as a function of the verb
def v_SO(sent, token, index, k):
    #definitons
    conds_obj_good = [{"deprel": obj_or_iobj, "lemma": no_weak_pronoun, is_not_any_of: [{feats_include: {"PronType": "Rel"}},{"upos": "ADP"}, {"upos":"ADJ"},{"upos":"ADV"}] , has_no_sons: [{"upos": "ADP"}, {"deprel": "case"}, {"deprel": "cop"}, {"deprel": "mark"}]}]
    conds_wsubj_true = [{"deprel": "nsubj", "lemma": no_weak_pronoun, is_not: {feats_include: {"PronType": "Rel"}}, has_no_son: {"deprel": "cop"}}]

    if token.get("upos") != "VERB":
        return False
        # search for subject
    #print("SO_VERB", token.get("form"))
    subj=0
    obj=0
    for word in sent:
        if word.get("head") == token.get("id"):
            # print("a", word.get("form"))
            if check_conds(sent, word, word.get("id") - 1, conds_wsubj_true[0]):
                subj= word
                # print("subj:", subj.get("form"))
                break
            else:
                pass
    if not subj:
        # print("nosubj")
        return False
    # search for object
    for word in sent:
        if word.get("head") == token.get("id"):
            # print("b:", word.get("form"))
            if check_conds(sent, word, word.get("id") - 1, conds_obj_good[0]):
                obj = word
                # print("obj:", obj.get("form"))
                break
            else:
                pass
    if not obj:
        return False
    # print(sent.metadata.get("text"))
    # print(obj.get("id"),subj.get("id"))
    if obj.get("id")>subj.get("id"):
        # print(f"subj: {subj.get('form')} obj:{obj.get('form')}, verb:{token.get('form')}")
        # print("subj comes before object, SO")
        return True
    else:
        return False

def v_OS(sent, token, index, k):
    #definitons
    conds_obj_good = [{"deprel": obj_or_iobj, "lemma": no_weak_pronoun, is_not_any_of: [{feats_include: {"PronType": "Rel"}},{"upos": "ADP"}, {"upos":"ADJ"}, {"upos":"ADV"}] , has_no_sons: [{"upos": "ADP"}, {"deprel": "case"}, {"deprel": "cop"}, {"deprel": "mark"}]}]
    conds_wsubj_true = [{"deprel": "nsubj", "lemma": no_weak_pronoun, is_not: {feats_include: {"PronType": "Rel"}}, has_no_son: {"deprel": "cop"}}]

    if token.get("upos") != "VERB":
        return False
        # search for subject
    # print("OS_VERB", token.get("form"))
    subj=0
    obj=0
    for word in sent:
        if word.get("head") == token.get("id"):
            # print("a", word.get("form"))
            if check_conds(sent, word, word.get("id") - 1, conds_wsubj_true[0]):
                subj= word
                #print("subj:", subj.get("form"))
                break
            else:
                pass
    if not subj:
        # print("nosubj")
        return False
    # search for object
    for word in sent:
        if word.get("head") == token.get("id"):
            # print("b:", word.get("form"))
            if check_conds(sent, word, word.get("id") - 1, conds_obj_good[0]):
                obj = word
                # print("obj:", obj.get("form"))
                break
            else:
                pass
    if not obj:
        return False
    # print(sent.metadata.get("text"))
    if obj.get("id")<subj.get("id"):
        # print(f"subj: {subj.get('form')} obj:{obj.get('form')}, verb:{token.get('form')}")
        # print("obj comes before subj, OS")
        return True
    else:
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
                raise TypeError(f"conditions must be a list of dicts, got {conds} instead, which is {type(conds)}")
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


    #return llista
    return count


#returns a list of sentences where a certain condition is met
#
def check_conllu_for_conditions_v3(filename, conditions, max_l=100, printf=False, custom_id=False):
    conllu_parse= file_to_conllu(filename)
    llista =[]
    count=0 #counts how many times the conditions are fulfilled in the whole corpus
    if not isinstance(conditions, list):
        for conds in conditions:
            if not isinstance(conds, dict):
                raise TypeError(f"conditions must be a list of dicts, got {conds} instead, which is {type(conds)}")
    #print(f'dict of conds has {l} conditions')
    for num, sent in enumerate(conllu_parse):
        if len(llista) > max_l:
            break
        times=len(check_sent_for_conditions(sent, conditions, printf))
        if times:
            if custom_id and "custom_id" in sent.metadata.keys():
                llista.append((times,sent.metadata["custom_sent_id"]))
            else:
                llista.append((times, sent.metadata["sent_id"]))
    return llista
    #return count


# for a condition returns a list of dictionaries of all the sentences, incl content, that fulfill it in the file
def check_conllu_for_conditions_v4(filename, conditions, max_l=100, printf=False, custom_id=True):
    conllu_parse= file_to_conllu(filename)
    llista =[]
    count=0 #counts how many times the conditions are fulfilled in the whole corpus
    if not isinstance(conditions, list):
        for conds in conditions:
            if not isinstance(conds, dict):
                raise TypeError(f"conditions must be a list of dicts, got {conds} instead, which is {type(conds)}")
    #print(f'dict of conds has {l} conditions')
    for num, sent in enumerate(conllu_parse):
        if len(llista) > max_l:
            print("max n of examples erreicht")
            break
        matches= check_sent_for_conditions(sent, conditions, printf)
        times=len(matches)
        if times:
            d= {"times": times, "matches":matches, "sent_text": sent.metadata["text"], "filename": filename, "eval_date": datetime.datetime.now()}
            if custom_id:
                if "custom_sent_id" in sent.metadata.keys():
                    d["custom_sent_id"] = sent.metadata["custom_sent_id"]
            else:
                d["sent_id"] = sent.metadata["sent_id"]
            llista.append(d)
    print(f"\tfound {len(llista)} sentences")
    return llista




#just counts how many times a condition is met in the corpus
def check_conllu_for_conditions2(filename, conditions, printf=False):
    conllu_parse= file_to_conllu(filename)
    llista =[]
    count=0 #counts how many times the conditions are fulfilled in the whole corpus
    if not isinstance(conditions, list):
        for conds in conditions:
            if not isinstance(conds, dict):
                print("error this is not a list of dicts")
                print("conditions:", conditions)
                print(f'{conds} is a {type(conds)}')
    #print(f'dict of conds has {l} conditions')
    for sent in conllu_parse:
        count= count + len(check_sent_for_conditions(sent, conditions, printf))
    #return llista
    return count

def check_sent_for_conditions(sent, conditions, printf=False):
    if printf:
        print(sent.metadata["text"], "length", len(sent))
    # add converting a text sent to a conllu parsed sent
    n = len(sent)
    l = len(conditions)
    counter=0
    token_list=[]
    #remove this condition, it is also tested as part of the for loop:
    #print(f'{l} conditions, {n} len(sent)')
    for j, token in enumerate(sent):
        if printf:
            print(token.get("form"))
        if j >= n-l:
            return token_list
            #return counter
        else:
            for i, cond in enumerate(conditions):
                if printf:
                    print("\tchecking cond", i, "on token", sent[j+i].get("form"))
                #conditions is a list of dictionaries of conditions to check on consecutive words
                #each cond is a dictionary of conditions to check on one word
                if check_conds(sent, sent[j+i], j, cond):
                    #print(f'***condition {cond} met, token {sent[j+i]}')
                    if i == len(conditions)-1:
                        token_list.append(token.get("form"))
                        counter+=1
                        if printf:
                            print(f'\t\t ****match in sentence {sent.metadata["sent_id"]}')
                            print("\t\tcontext:",sent.metadata["text"])
                        for k in range(l):
                            if printf:
                             print(f'\ttoken {sent[j+k].get("form")} fulfills {conditions[k]}\n')
                             #print(f'{sent[j+k]} h:{sent[j+k].get("head")} {sent[j+k+1].get("id")}')

                            pass
                else:
                    if printf:
                        print(f'\t\ttoken {sent[j+i]["form"]} doesnt fulfill {cond}')
                    break
    #print("i am using counter conds rn")
        #count= counter_conds(conllu_parse, conditions)
    return token_list
    #return counter


#receives two lists of conditions (which are acutally dictionaries of conditions, in the shape:
# {'#nsubj': [{'deprel': 'nsubj'}], 'nsubj + SV': [{'deprel': 'nsubj', 'head': <function head_greater_than_id at 0x7f054bfffec0>}] }
#returns a cross product of the intersections between each possible pair of conditions, this is, when both are met
#nice
#this is an old function, deprecated!!
def merge_conds_dicts(condict1, condict2):
    mega_dict= {}
    for name1,cond1 in condict1.items():
        for name2, cond2 in condict2.items():
            l=[]
            for c1 in cond1:
                for c2 in cond2:
                    # unir condicions
                    z = c1 | c2
                    #si hi ha condicions incompatibles s hi afegeix una condicio impossible
                    for intersecting_keys in set(c1.keys()).intersection(set(c2.keys())):
                        print("intersecting keys", intersecting_keys)
                        print("values1:", c1[intersecting_keys], "values2:", c2[intersecting_keys])
                        if type(c1[intersecting_keys]) is not type(c2[intersecting_keys]):
                            print("Err when merging condtitions, values not of the same type:")
                            print("type1:", type(c1[intersecting_keys]))
                            print("type2:", type(c2[intersecting_keys]))
                            return {}
                        elif type(c1[intersecting_keys]) is str or type(c1[intersecting_keys]) is dict:
                            if c1[intersecting_keys] != c2[intersecting_keys]:
                                print("****non compatible conditions\n")
                                print("condition 1\n:", c1[intersecting_keys])
                                print("condition 2\n:",c2[intersecting_keys])
                                z = {intersecting_keys:"impossible"}
                                l.append(z)
                        #this is the case with conditions such as has_sons : [{"upos": "NOUN", "deprel": "nsubj"}]
                        # what it should do then is
                            elif type(c1[intersecting_keys]) is list:
                                print("ok we re son there")
                                return 0

                        else:
                            print("Error, merging conditions of wrong kind, wtf", print(type(c1[intersecting_keys])))
            mega_dict.update({name1 + "__und__" + name2 : l})

    for cross_name, cross_cond in mega_dict.items():
        print(cross_name, "::::", cross_cond)
    return mega_dict



# this function takes a list of conllu files and prints them together into 1 valid conllu file
# it also renames the sentences in the list so that the number is coherent
def conllu_merger(file_list, output_file, repeated_articles= False):
    mega_conllu = ""
    macro_conllu_string= ""
    for file in file_list:
        if not file.endswith(".conllu"):
            print(f"error, {file} is not a conllu file yet")
            return 0
        try:
            with open("analysed_corpus/" + file, "r") as f:
                text = f.read()
            mega_conllu += text
        except Exception as e:
            print(f"error with {file} ", e)
        else:
            pass
    sent_id_counter=0
    unique_url_pairs=[]
    all_pairs = []
    total_counter=0
    unique_counter=0
    if not repeated_articles:
        for i, sent in enumerate(parse(mega_conllu)):
            first=0
            # CHECKING FOR REPEATED ARTICLES
            if not "url" in sent.metadata.keys():
                print("URL info missing, can't check for repeated articles")
                break
            else:
                pair = (sent.metadata["url"], sent.metadata["article_id"])
                # tenim aquesta url en general?
                if pair not in all_pairs:
                    total_counter += 1
                    first =1
                    all_pairs.append(pair)
                # si l url no la tnim encara, afegim el parell
                if pair[0] not in [item[0] for item in unique_url_pairs]:
                    unique_url_pairs.append(pair)
                    unique_counter += 1
                # si el parell no es el primer cop q hi ha la url
                if pair not in unique_url_pairs:
                    if first:
                        for item in all_pairs:
                            if pair[0] == item[0] and pair[1] != item[1]:
                                print(f"url {pair[0]}, both under {pair[1]} and {item[1]}\n")
                    continue
                else:
                    sent.metadata.update({"sent_id": str(sent_id_counter).zfill(6)})
                    sent_id_counter = sent_id_counter + 1
                    macro_conllu_string = macro_conllu_string + sent.serialize()


    else:
        print("we re allowing repeated articles")
        for i, sent in enumerate(parse(mega_conllu)):
            sent.metadata.update({"sent_id_custom": str(sent_id_counter).zfill(6)})
            sent_id_counter = sent_id_counter + 1
            macro_conllu_string = macro_conllu_string + sent.serialize()
    print("Total nr of articles", total_counter, "total nr of unique articles", unique_counter)

    # Path("analysed_corpus/").mkdir(parents=True, exist_ok=True)
    with open("analysed_corpus/" + output_file, "w") as f:
        f.write(macro_conllu_string)

# enter list of topics + codi + tipus
# list of files with that topic (1 per topic, the biggerst one) and codi are returned
def conllu_files_list(llista_temes, codi, tipus):
    llista_arxius=[]
    for tema in llista_temes:
        print("adding", tema)
        if not glob.glob(f"analysed_corpus/{codi}{tipus}_corpus_*_{tema}*.conllu"):
            #raise Exception(f"File for topic {codi}{tipus}_corpus_*_{tema}*.conllu not found.")
            print(f"!!!! {codi}{tipus}_corpus_*_{tema}*.conllu not found")
        elif len(glob.glob(f"analysed_corpus/{codi}{tipus}_corpus_*_{tema}*.conllu")) > 0:
            topic_files=glob.glob(f"analysed_corpus/{codi}{tipus}_corpus_*_{tema}*.conllu")
            topic_files.sort(reverse=True)
            corpuspath = topic_files[0]
            corpusfile = corpuspath.split("/")[-1]
            llista_arxius.append(corpusfile)
    return llista_arxius



def corpus_merger(llista_arxius, output_file, repeated_articles= False):
    baby_json= []
    url_list= []
    for infile in llista_arxius:
        list_of_dicts= []
        with open("data/"+infile, "r") as in_file:
            data = json.load(in_file)
        #print(data[0].keys())
        interesting_keys= ["url", "custom_id", "batch_id", "corpus", "file"]
        for item in data:
            item["file"]=infile
            if item["url"] in url_list:
                continue
            else:
                url_list.append(item["url"])
                list_of_dicts.append({k: item[k] for k in interesting_keys})
        print(infile, len(data), "unique:",len(list_of_dicts))
        baby_json.extend(list_of_dicts)
        url_list.extend([item["url"] for item in list_of_dicts])

    with open("corpus/"+output_file, "w") as outfile:
        json.dump(baby_json, outfile, ensure_ascii=False)


# enter list of topics + codi + tipus
# list of json files with that topic (1 per topic, the biggerst one) and codi are returned
def corpus_files_list(llista_temes, codi, tipus):
    llista_arxius = []
    for tema in llista_temes:
        print("adding corpus file", tema)
        if not glob.glob(f"data/{codi}{tipus}_corpus_*_{tema}*.json"):
            # raise Exception(f"File for topic {codi}{tipus}_corpus_*_{tema}*.conllu not found.")
            print(f"!!!! {codi}{tipus}_corpus_*_{tema}*.json not found")
        elif len(glob.glob(f"data/{codi}{tipus}_corpus_*_{tema}*.json")) > 0:
            topic_files = glob.glob(f"data/{codi}{tipus}_corpus_*_{tema}*.json")
            topic_files.sort(reverse=True)
            corpuspath = topic_files[0]
            corpusfile = corpuspath.split("/")[-1]
            llista_arxius.append(corpusfile)
    return llista_arxius