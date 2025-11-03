from conllu_test import file_to_conllu, check_conds
import time
import pandas as pd
from pathlib import Path


#returns stats for the file: amount of words, amount of sentences
def conllu_file_stats(file):
    d={}
    v=[]; w=[]
    words=0
    if not file_to_conllu(file):
        print("error file empty, or file not conllu")
        return {}
    for item in file_to_conllu(file):
        words=words+len(item)
    d["words"]=words
    d["sentences"]= len(file_to_conllu(file))
    d["av. sentence length"]=d["words"]/d["sentences"]
    #calculate tree depth
    for sent in file_to_conllu(file):
        h= sent_tree_height(sent)
        #print(sent.metadata["sent_id"], h)
        v.append(h)
        w.append(h/len(sent))

    #print(len(v), len(file_to_conllu(file)))
    d["av. tree height"]= sum(v)/len(v)
    d["max tree height"]= max(v)
    d["tree height / sent length"]= sum(w)/len(w)
    return d



# computes the height(distance to root) of a token in a sentence recursively
# used for the stats
def height(token, sent, v):
    h= v[int(token["id"])-1]
    if h>len(sent):
        print("error, max height surpassed in", sent.metadata["custom_sent_id"])
        return h
    if token["head"] ==0:
        return h
    else:
        v[int(token["id"])-1] = height( sent[int(token["head"])-1], sent, v) + 1
        h = v[int(token["id"])-1]
    return h

#used for the file stats
def sent_tree_height(sent):
    f0=1
    for token in sent:
        if token["head"] ==0:
            f0=0
            break
    if f0:
        print("error, there is no root", sent.metadata["custom_sent_id"])
        return 0
    v = [0]* len(sent)
    for token in sent:
        height(token, sent, v)
    v.sort()
    #print("checking depth of", sent.metadata["custom_sent_id"])
    return v[-1]


# geta a conllu file list, it prints out the frequencies of all the different categories in different files
def file_freqs_eval(file_list):
    file_to_conllu(file_list[0])
    conllu_cats = file_to_conllu(file_list[0])[0][0].keys()
    print(conllu_cats)
    stupid_categories= ['id', 'misc', "head", "deps"]
    t0=time.time()
    for cat in conllu_cats:
        t1=time.time()
        print("We re starting with:", cat)
        if cat in stupid_categories:
            print(f"{cat} skipped")
            continue
        res_col=[]
        outfile=f"corpus_freqs_{cat}.csv"
        for file in file_list:
            #res_col.append(conllu_file_freqs(file, "upos", rel=False))
            res_col.append(conllu_file_freqs(file, cat, rel=True))
        #print("*"*16, cat, "*"*16, res_col)
       # check if the folder exists, else create it
        Path("eval/freq/").mkdir(parents=True, exist_ok=True)
        with open("eval/freq/"+outfile, "w") as f:
            df=pd.DataFrame(res_col)
            df.to_csv(f, sep=",", index=False)
        print(f"{cat} completed :) loop took {time.time()-t1}s, running for {time.time()-t0} seconds \n")
    return 0

# geta a conllu file list, it prints out the frequencies of all the different categories in different files
# and also an eval set, a list of dictionaries, pairs of a condition and its name
#prefix
def file_freqs_eval_filtered_by_conds(file_list, eval_set, prefix="filtered"):
    file_to_conllu(file_list[0])
    conllu_cats = file_to_conllu(file_list[0])[0][0].keys()
    print(conllu_cats)
    stupid_categories= ['id', 'misc', "head", "deps"]
    t0=time.time()
    for cat in conllu_cats:
        t1=time.time()
        print("We re starting with:", cat)
        if cat in stupid_categories:
            print(f"{cat} skipped")
            continue
        res_col=[]
        outfile=f"{prefix}_corpus_freqs_{cat}.csv"
        for file in file_list:
            d_res= conllu_file_freqs(file, cat, rel=False)
            d_res.update({ "cond_series": "none"})
            res_col.append(d_res)
            for i, condition in enumerate(eval_set):
                for keys, values in condition.items():
                    d_res= conllu_file_freqs(file, cat, conds= values, name_cond= keys, rel=False)
                    d_res.update({ "cond_series": i})
                    res_col.append(d_res)
        #print("*"*16, cat, "*"*16, res_col)
       # check if the folder exists, else create it
        Path("eval/freq/").mkdir(parents=True, exist_ok=True)
        with open("eval/freq/"+outfile, "w") as f:
            df=pd.DataFrame(res_col)
            df.to_csv(f, sep=",", index=False)
        print(f"{cat} completed :) loop took {time.time()-t1}s, running for {time.time()-t0} seconds \n")
    return 0


#computes for each file all of the freqs of the different values it might have
# BUT it allows us to include a condition (since i  want to get rid of conditions as lists of dictionaries, since i only use them with one dictionary, it only works on the first element of the list :))
def conllu_file_freqs(filename, conllu_cat, conds=0, name_cond= "", rel=False):
    data = file_to_conllu(filename)
    d={}
    w=0
    d["filename"]= filename
    d["category"]= conllu_cat
    if not conds:
        d["conds"] = "-"
    else:
        if name_cond:
            d["conds"] = name_cond
        else:
            d["conds"] = conds[0]
    if rel:
        d["rel"]= 1
    else:
        d["rel"] = 0
    if not conllu_cat in data[0][0].keys():
        print(f"error {conllu_cat} is not a valid key.\n Valid keys are:",data[0][0].keys())
    else:
        if not conds:
            for sent in data:
               for j, token in enumerate(sent):
                    w+=1
                    #print(cat, token, type(token))
                    # I am turning token[cat] into a string bc when cat= feats it is a dictionary :/
                    t= token[conllu_cat]
                    t=str(t)
                    if t in d.keys():
                        d[t]+=1
                    else:
                        d[t]=1
        elif isinstance(conds[0], dict):
            for sent in data:
               for j, token in enumerate(sent):
                   if check_conds(sent, token, j, conds[0]):
                        w+=1
                        #print(cat, token, type(token))
                        # I am turning token[cat] into a string bc when cat= feats it is a dictionary :/
                        t= token[conllu_cat]
                        t=str(t)
                        if t in d.keys():
                            d[t]+=1
                        else:
                            d[t]=1
                   else:
                       pass
        else:
            print("ERR: conds[0] not a dict :-( ")
    if rel:
        for key, value in d.items():
            try:
                int(d[key])
            except:
                pass
            else:
                d[key] = 100*int(d[key])/w
        d["rel"]= w
    #print(d)
    return d
