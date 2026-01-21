from conllu_test import file_to_conllu, check_conds, check_conllu_for_conditions_v3, check_conllu_for_conditions2, check_conllu_for_conditions_v4
import time
import pandas as pd
from pathlib import Path
import json
import datetime

# FUNCTION 1 :input dict of conditions
# max ex refers to the maximum of examples it will include in the summary
#output: list of condition dictionaries, ready to json load
def eval_conds(d_conds, file, max_ex=100, custom_id= False):
    list=[]
    t0 = time.time()
    for name, cond in d_conds.items():
        t1=time.time()
        print(f"\tEvaluating {name} on {file}")
        results={"filename": file, "eval_series":0, "cond_name": name,  "matches":check_conllu_for_conditions2(file, cond, printf=False), "cond_content": cond, "examples":check_conllu_for_conditions_v3(file, cond, max_l=max_ex, custom_id=custom_id), "eval_date": datetime.datetime.now()}
        for key in results:
            results[key] = str(results[key])
        list.append(results)
        print(f"\t \tEvaluated {name} on {file}, it took {time.time()-t1}")
    print(f"done with list, it took {time.time()-t0}")
    return list

#returns a list of dictionaries for each condition,
def eval_conds_extra_files(cond, file, name, max_ex=500, custom_id= False):
    # achtung check_conllu_for_conditions_v4 already returns a list of dicts
    results = check_conllu_for_conditions_v4(file, cond, max_l=max_ex)
    total_nr = check_conllu_for_conditions2(file, cond, printf=False)
    for d in results:
        d["matches"] = str(total_nr)
        d["cond_name"] = name
    return results

# FUNCITON 2: input: list of result dictionaries + name of the file the results should be printed in
# checks that the keys are the ones htat shoud be too
# If return_res is false, the dict gets printed in a json file, else it is returned
def print_eval_log(jlist, outfile, return_res=True):
    # check if the folder exists, else create it
    Path("eval/").mkdir(parents=True, exist_ok=True)

    outpath = "eval/"+outfile
    standard_dict = {"filename":0, "cond_name":"", "cond_content":0, "matches":0, "eval_date":0 , "examples": [], "eval_series":0, "cond_nr": 0}
    for result in jlist:
        #print("this is going ot be my dict: \n", result)
        dres= dict(result)
        if dres.keys() != standard_dict.keys():
            print(f"error keys dont match:\n {dres.keys()}\n vs. \n{standard_dict.keys()}")
            return 0
    if not return_res:
        with open(outpath, "w") as f:
            json.dump(jlist, f)
    else:
        return jlist

# list of condition lists comes in,
# file list comes in
# evaluates conditions on ht efiles and prints the result in  outfile.tsv, can be opened with libre office
def eval_pipeline(list_of_eval_sets, file_list, outfile, basic_run=True, extra_eval_files= True):
    t0=time.time()
    thyme = str(datetime.datetime.now())[:-7]

    res_col=[]
    conds_count=0
    if basic_run:
        for file in file_list:
            for num, eval_series in enumerate(list_of_eval_sets):
                print(f"Evaluating list {num+1} of {len(list_of_eval_sets)} on {file}")
                res_l=eval_conds(eval_series, file, max_ex=100, custom_id=True)
                for result in res_l:
                    #adding a eval series number to the results from the same list of conditions (like nsubj list)
                    result.update({"cond_nr": conds_count})
                    result.update({"eval_series": num})
                    res_col.append(result)
                    conds_count+=1
        evals = json.dumps(print_eval_log(res_col, outfile, return_res=True))
        print("***SUCCESSFUL RUN***")
        print(f" {conds_count} evaluations done in {time.time() - t0} s, av. time {(time.time() - t0) / conds_count} s")
        please = json.loads(evals)
        with open("eval/" + outfile, "w") as f:
            df = pd.DataFrame(please)
            df.to_csv(f, sep="\t", index=False)

    if extra_eval_files:
        print("going for extra printing files to each condition")
        for num, eval_series in enumerate(list_of_eval_sets):
            for name, cond in eval_series.items():
                sentences_res= []
                for file in file_list:
                    print(f"Evaluating cond {name} on {file}")
                    sentences_res.extend(eval_conds_extra_files(cond, file, name, max_ex=200, custom_id=True))

                foldername= file_list[0][0:3] +"_"+ thyme
                filename= file_list[0][0:3]+"_"+name+".csv"
                Path(f"eval_sents/{foldername}").mkdir(parents=True, exist_ok=True)
                with open(f"eval_sents/{foldername}/{filename}", "w") as f:
                    print("printing to ", filename)
                    df = pd.DataFrame(sentences_res)
                    df.to_csv(f, sep="\t", index=False)

    return 0












#returns a list of all the values for the conllu feateures present in the corpus
def conllu_possible_values():
    good_conllu_keys=["upos", "xpos", "feats", "deprel"]

    d_categories={}
    for cat in good_conllu_keys:
        d_categories[cat]=conllu_file_freqs("tv3_corpus.conllu", cat, rel=True)
        d_categories[cat].update(conllu_file_freqs("KI_corpus.conllu", cat, rel=True))
        del d_categories[cat]["filename"]
        del d_categories[cat]["category"]
        del d_categories[cat]["rel"]
        d_categories[cat]= list(d_categories[cat].keys())
        print(cat, d_categories[cat], "\n\n")
    return d_categories







#returns stats for the file: amount of words, amount of sentences
def conllu_file_stats(file):
    d={}
    v=[]; w=[]
    words=0
    conllu_file = file_to_conllu(file)
    if not conllu_file:
        print("error file empty, or file not conllu")
        return {}
    #
    # print(conllu_file[0].metadata.keys())
    # for key in conllu_file[0].metadata.keys():
    #     print(key, conllu_file[0].metadata[key])
    # print(conllu_file[0][0].keys())
    # for key in conllu_file[0][0].keys():
    #     print(key, conllu_file[0][0][key])

    for sent in conllu_file:
        words=words+len(sent)
    d["words"]=words
    d["sentences"]= len(conllu_file)
    d["av. sentence length"]=d["words"]/d["sentences"]
    # number of articles
    art_ids = {"a"}
    for sent in conllu_file:
        art_ids.add(sent.metadata["article_id"])
    d["articles"]= len(art_ids)
    d["sentences/article"] = d["sentences"]/d["articles"]
    #calculate tree depth
    for sent in conllu_file:
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



# computes for each file all of the freqs of the different values it might have
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



#THE OTHER NOT SO USED EVALUATION FUNCTIONS
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

