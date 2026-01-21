from openai import OpenAI
import time
import copy
import json
from spacy_conllu import remove_urls
import glob
from batch_creator import tv3_to_batch
import os.path
import html
from cleaning_tools import KI_r2c, gen_r2c, corpus_to_data

# API configuration
api_key = '89d3827b18a05873a7112804bc3fa1fb' # SAIA API key, gültig bis märz 25
base_url = "https://chat-ai.academiccloud.de/v1"
#model = "meta-llama-3.1-8b-instruct" # Choose any available model
  
# Start OpenAI client
client = OpenAI(
    api_key = api_key,
    base_url = base_url
)

#reads a batch file and returns a list of dicts ready to be read
def batch_reader(filename):
    prompts=[]
    with open(filename, 'r') as infile:
        for entry in infile:
            entrada= json.loads(entry)
            #print(entrada)
            did={}
            did["prompt"]=entrada["body"]["input"]
            did["max_tokens"]= entrada["max_tokens"]
            #did["invented"] = "fun"
            did["url"]= entrada["url"]
            did["custom_id"]=entrada["custom_id"]
            did["batch_id"] = entrada["batch_id"]
            did["model"]= entrada["body"]["model"]
            #prompts.append(json.loads(entry))
            prompts.append(did)
    return prompts

    
models='''meta-llama-3.1-8b-instruct 
openai-gpt-oss-120b 
meta-llama-3.1-8b-rag 
llama-3.1-sauerkrautlm-70b-instruct 
llama-3.3-70b-instruct 
gemma-3-27b-it 
teuken-7b-instruct-research 
mistral-large-instruct 
qwen3-32b 
qwen2.5-coder-32b-instruct 
codestral-22b 
internvl2.5-8b 
qwen2.5-vl-72b-instruct'''
models_list = models.split(" \n")

models_bons= ["llama-3.3-70b-instruct", "gemma-3-27b-it", "mistral-large-instruct"]

# makes a series of queries to the llm_model
# returns a list of dicts, 
def ask_llm(prompts, max_queries, value, waiting_time=False, printf=True):
    chat_completions =[]
    t0 = time.time()
    n= min(len(prompts), max_queries)
    for i in range(n):
        prompts_filtered =  {k: v for k, v in prompts[i].items() if "id" not in k}
        del prompts_filtered["url"]
        #answer= {}
        t1= time.time()
        try:

            print(f"Trying query nr {i}: \n {prompts_filtered}")
            #answer=dict(client.completions.create(**prompts_filtered, model= llm_model))
            answer = dict(client.completions.create(**prompts_filtered))
        except Exception as e:
            print(f"Query nr {i} failed.")
            print(e)
            if waiting_time:
                print(f"sleeping")
                value +=1
                time.sleep(60)
                #chat_completions.append(client.completions.create(**prompts[i], model= llm_model))
                new_list= [prompts[i]]
                ask_llm(new_list, max_queries, value, waiting_time=True, printf=True)
                print("nr of times slept:", value)
                if value >= 2:
                    print("KI is not responding")
                    return 0
        else:
            t2=time.time()
            answer["completion_time"]=t2-t1
            #answer["prompt"]=prompts[i]["prompt"]
            answer.update(prompts[i])
            chat_completions.append(answer)
            print(f"Query nr {i} successful, took {t2-t1} seconds, this loop has been running for {time.time()-t0}s.")
    print(f"Total successful queries: {len(chat_completions)} \n Total ex. time= {time.time()-t0}")
    return chat_completions
    
#used in print_completions to clean the output of ask_llm, make each datapoint an easy to access, easy to print dictionary 
def reestructure_chat_completions(chat_completions):
    chat_completions_clean= copy.deepcopy(chat_completions)
    for i,completion in enumerate(chat_completions_clean):
        completion.update(dict(completion["choices"][0]))
        completion.pop("choices")
        completion.update(dict(completion["usage"]))
        completion.pop("usage")
        completion["QC_text"]= ""
        completion["corpus"]= ""
    return chat_completions_clean

#remove annoying headers and titles, also ensure that there is no incomplete sentence at the end
#

#enters text, returns text
# cleans out everything surrounded by ** ** and everything after the last .
# also removes every sentence that includes "\n*"
def KI_text_cleaner(text):

    text = html.unescape(html.unescape(text))
    if not isinstance(text, str):
        print("error, KI answer is not a string")
        return ""
    else:
        cleaned_text1 = ""
        # elimina titols
        for i, paragraph in enumerate(text.split("\n")):
            #print(i, paragraph)
            if not paragraph:
                #print("1 skipped '", paragraph, "'")
                continue
            if len(paragraph.strip()) < 2:
                #print("1.5 skipped '", paragraph, "'")
                continue
            if paragraph.strip()[-1].isalnum() or paragraph.strip()[-1] == ":":
                #print("2skipped '", paragraph, "'")
                continue

            if paragraph.strip()[1] == "*":
                #print("3skipped '", paragraph, "'")
                continue
            # else add the paragraph
            # PARAGRAPHS ARE PRESERVED
            if not cleaned_text1:
                cleaned_text1 = paragraph
            else:
                cleaned_text1 = cleaned_text1 + "\n" + paragraph
                #print(i, paragraph)
        cleaned_text = cleaned_text1
        #remove urls
        text= remove_urls(cleaned_text1)
        #delete text between the even "**" positions, as they are subtitles
        pieces=text.split("**")
        if len(pieces)==1:
            cleaned_text=pieces[0]
        elif len(pieces) > 1:
            for i, piece in enumerate(pieces):
                if i%2==0:
                    cleaned_text=cleaned_text+piece
            try:
                cleaned_text.rindex(".")
            except:
                print("problem, no colon after the laast star")
                return ""
        try:
            cleaned_text.rindex(".")
        except:
            print("err, no colon in the whole KI text")
            return ""
        #Elimina el q hi ha darrere de l ultim "."
        cleaned_text= cleaned_text[:cleaned_text.rindex(".")]+"."

        cleaned_text2=""
        # Elimina possibles enumeracions
        # filter all problematic combinations of characters that identify KI bad sentences
        problematic_chars = [":", "!", "]", "/", "*", "?","EFE", "ACN","El Punt Avui", "Vilaweb",  "preguntes:"]
        for sentence in cleaned_text.split(". "):
            if bool("(" in sentence) ^ bool(")" in sentence):
                print("uncomplete parenthesis found: ", sentence)
                break
            flag=0
            for char in problematic_chars:
                if sentence.find(char) != -1:
                    flag=1
                    break
            if flag == 1:
                print(f"\t {char} found in sentence: {sentence}, skipping")
                continue

            # check if there at least one alphanumeric character in the sentence
            flag=1
            for character in sentence:
                if character.isalpha():
                    flag=0
                    break
            if flag==1:
                print(f"\t Deleting non-text sentence: {sentence}")
                continue
            else:
                cleaned_text2=cleaned_text2+sentence+". "

        #cleaned_text2= clean_text_conllu(cleaned_text2)
        return cleaned_text2





#enters one complex answers dict, cleans it and prints a 1-level dictionary ouptput to json 
def print_completions(chat_completions, filename):
    chat_completions_clean=reestructure_chat_completions(chat_completions)
    with open(filename, "w") as outfile:
        json.dump(chat_completions_clean, outfile, ensure_ascii = False)



# creates the batch file, reads it, etc
# again codi should be str, llista_temes is a dict
def KI_corpus_generator(codi, llista_temes, model):
    n_model = model

    # 1- generate batch file
    corpus_list = []
    t0 = time.time()
    for tema in llista_temes.keys():
        print(tema)
        # read the data file
        if not glob.glob(f"data/{codi}tv3_corpus_*_{tema}.json"):
            raise Exception(f"File for topic {codi}tv3_corpus_*_{tema}.json not found.")
        else:
            if not len(glob.glob(f"data/{codi}tv3_corpus_*_{tema}.json")) >= 1:
                raise Exception("what is going on?")
            tematic_jsons = glob.glob(f"data/{codi}tv3_corpus_*_{tema}.json")
            print(tematic_jsons)
            tematic_jsons.sort(reverse=True)
            corpuspath = tematic_jsons[0]
            corpusfile = corpuspath.split("/")[-1]

            if len(glob.glob(f"data/{codi}tv3_corpus_*_{tema}.json")) > 1:
                print("ACHTUNG mehrere files zum thema", tema, tematic_jsons)
                print("picked", corpusfile)


        # corpusfile=f"{codi}tv3_corpus_{len(scraped_data)}_{tema}.json"
        # corpuspath= "data/"+corpusfile
        with open(corpuspath, "r") as f:
            scraped_data = json.load(f)
        batchfile = f'batch-prompts_{len(scraped_data)}_{tema}.jsonl'
        batchpath = "data/" + batchfile

        if os.path.isfile(corpuspath):
            tv3_to_batch(corpuspath, batchpath, model)

        # 2 ask KI to generate parallel corpus from the prompts in the jsonl batchfile
        printf = True
        value = 0  # this will be deleted, KI never sleeps, AI rate never exceeded
        t1 = time.time()
        if printf:
            print("*" * 16)
            print("Generating answers to topic", tema)
            print("*" * 16)

        prompts = batch_reader(batchpath)
        l = len(prompts)
        llm_answers = ask_llm(prompts, waiting_time=False, max_queries=l, value=value)

        KIfile = f"{codi}KI_corpus_{len(llm_answers)}_{tema}_{n_model}.json"
        KIpath = "data/" + KIfile
        corpus_list.append(KIfile)
        if printf:
            print("*" * 16)
            print(f"Time for {tema} iteration: ", (time.time() - t1) / 3600, "hours")
            print("av. time per prompt:", (time.time() - t1) / (1 + len(prompts)), "s")
            print("Total time so far", (time.time() - t0) / 3600, "hours")
            print("#prompts:", len(prompts), "#answers:", len(llm_answers))
            print("*" * 16)
        # giving the answers list of dictionary structure
        chat_completions_clean = reestructure_chat_completions(llm_answers)
        # cleaning the answers
        for i, completion in enumerate(chat_completions_clean):
            # cleaning step to make the corpus out of the raw data
            completion["corpus"]= KI_r2c(gen_r2c(completion["text"]))

            # extracing data from the corpus
            completion["QC_text"] = corpus_to_data(completion["corpus"])
            if not completion["QC_text"]:
                print("cleaning KI text made it empty")
                continue

        # printing the answers
        with open(KIpath, "w") as outfile:
            json.dump(chat_completions_clean, outfile, ensure_ascii=False)

        print("saving to: ", KIpath)