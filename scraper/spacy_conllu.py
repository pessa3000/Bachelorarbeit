#!/usr/bin/env python

#analitza text en catala fent servir l spacy i el guarda en format conllu
#aquest funcio es pot executar de la manera seguent :D
# ./spacy_to_conll text.txt > prova_conll.conllu -> ja no,  me n he cansat

import os
import glob
import json
import time
from conllu import parse
import spacy
import re
from fast_langdetect import detect


# function to remove URLS :)
def remove_urls(text, replacement_text=""):
    # Define a regex pattern to match URLs
    url_pattern = re.compile(r'https?://\S+|www\.\S+')

    # Use the sub() method to replace URLs with the specified replacement text
    text_without_urls = url_pattern.sub(replacement_text, text)

    return text_without_urls


#import spacy_conll
#receives a text, returns a string ready to print in the conllu format
def spacy_to_conll(text, lang= "ca"):
    if lang == "ca":
        nlp = spacy.load("ca_core_news_trf")
    nlp.add_pipe("conll_formatter",config={"include_headers": True}, last=True)
    doc = nlp(text)
    #print(type(doc))
    return doc._.conll_str




# returns a list of the repeated sentences in a text
def repeated_sentences_finder_text(text):
    l = text.split(". ")
    l = sorted(l)
    # sents= sorted({k: v for k, v in sorted(dic.items(), key=lambda item: item[1])})
    l_repeated = []
    c = 0
    repetitions = {}
    for i, item in enumerate(l):
        # print(item)
        if l[i] == l[i - 1] and l[i] != l[i - 2]:
            # print(l[i], "\n", l[i-1])
            l_repeated.append(l[i])
            l_repeated.append(l[i - 1])
            c = c + 2
        elif l[i] == l[i - 1] and l[i] == l[i - 2]:
            l_repeated.append(l[i])
            c= c+1

    #print(f"\t\tTotal sents{len(l)}, repeated {c}, {100 * c / len(l)} %")
    return l_repeated


# neteja el text per ajudar l spacy a trobar coses
# tmabe elimina les preguntes
# es fa servir en tots dos articles
def clean_text(content):
    if content == None:
        return None
    # remove urls that appear mostly in Ki texts
    content = remove_urls(content)
    # I modified this to keep the quotation marks, let's see :s
    #list_of_problematic_characters = ["\r", "\t", '"', "“"]
    list_of_problematic_characters = ["\r", "\t"]
    for c in list_of_problematic_characters:
        content = content.replace(c, "")
    #content = content.replace("”", ".")
    #paragraph check
    content2= ""
    for paragraph in content.split("\n"):
        if not paragraph:
            continue
        #paragraph = paragraph.strip()
        # HERE THE ENGLISH CHECK
        if detect(paragraph, model='lite', k=1)[0]["lang"] == "ca":
            flag = 0
        else:
            flag = 1
            for guess in detect(paragraph, model='full', k=3):
                if "ca" == guess["lang"] and guess["score"] > 0.1:
                    #print("suspicious but catalan", sentence)
                    # print(guess)
                    flag = 0
                    print("\t low confidence catalan paragraph", paragraph)
                    break
                else:
                    pass
            # print("eing", sentence)
        if flag == 1:
            print("\t removing non catalan sentence:'", paragraph, "'")
            # print(detect(sentence, model='lite', k=3))
            continue
        else:
            if not content2:
                content2 = paragraph
            else:
                content2 = content2 + "\n" + paragraph
    content= content2
    # paragraphs are removed from here on:
    content = content.replace("\n", " ")
    for i in range(10):
        content=content.replace("  ", " ")
     #eliminar les preguntes -> eliminatn els signes d exclamació
    cleaned_content = ""
    for sentence in content.split(". "):
        flag = 0
        if len(sentence) <=2:
            continue
        forbidden_characters= ["#", "="]
        for character in forbidden_characters:
            if sentence.find(character) != -1:
                flag=1

        # desperate attempt to save the good ":"
        if sentence.find(":") != -1:
            if len(sentence.split(":")[0].split(" ")) <=2:
                print("skipping problematic : ", sentence)
                continue
        if flag ==1:
            #print(f"{character} found in {sentence}")
            continue
            #check for question marks (different since they can replace .)
        if sentence.find("?") == -1:
           cleaned_content = cleaned_content + sentence + ". "
        # remove the question
        else:
            print("question mark found")
            print(sentence)
            cleaned_content = cleaned_content + sentence[sentence.find("?")+1:] + ". "
    #elimina dobles espais, dobles punts
    for i in range(7):
        cleaned_content= cleaned_content.replace("  ", " ")
        cleaned_content= cleaned_content.replace("..", ".")

    return cleaned_content

#old, just works w .txt files, returns .conllu file
def main(infile, outfile, lang= "ca"):
    infolder = "data"
    outfolder = "analysis"
    os.makedirs(infolder, exist_ok=True)
    os.makedirs(outfolder, exist_ok=True)

    with open(os.path.join(infolder, infile), "r") as file:
        content = file.read()
    content = clean_text(content)

    with open(os.path.join(outfolder, outfile), "w") as f:
        f.write(spacy_to_conll(content, lang))

#open a list of articles
#receives as input names of files in data and the name of the desired output file
# #returns nothing but prints a file with the conllu analysed file:)
def spacy_pipeline(infile, outfile, printf= True):
    with open("data/"+infile, "r") as file:
        article_list=json.load(file)
    macro_conllu_string=""
    if printf:
        t0=time.time()
        print("***\n"*2,f"Sending {infile} for spacy analysis :)")
    sent_id_counter = -1
    titles_list = []
    for i, article in enumerate(article_list):
        print("Spacy analysing article", i)
        # checking for repeated articles
        if "prompt" in article.keys():
            title = article["prompt"].split("\n")[0]
        elif "title" in article.keys():
            title = article["title"]
        if title in titles_list:
            print("Possibly duplicate article in infile:", article["prompt"].split(".")[0], "skipping")
            continue
            #print(article["prompt"].split(".")[0])
        titles_list.append(title)
        # checking if article is empty
        if not article["QC_text"]:
            print("\tERR: QC text is empty. Skipping", infile, "article nr", i)
            continue

        # checking if article is AI slop
        if len(repeated_sentences_finder_text(article["QC_text"])) > 0.1 * len(article["QC_text"].split(". ")):
            print(f'Ai slop detected, {100 * len(repeated_sentences_finder_text(article["QC_text"])) / len(article["QC_text"].split(". "))}% of repeated sentences. SKipping')
            continue

        t1=time.time()

        analysed_article=spacy_to_conll(article["QC_text"])

        #print(article["QC_text"])
        # reopen it using parse to change the metadata
        # clean the analysed files: delete empty sentences, delete sentences with autonodes or with no root
        parsed= parse(analysed_article)
        for num, sentence in enumerate(parsed):
            sent_id_counter = sent_id_counter + 1
            #delete empty sentences
            if not sentence.metadata.get("text"):
                print("\t\tempty sentence deleted in ", infile, "article nr", i, "nr", num)
                continue
            # delete sentences not starting with an uppercase letter

            # delete sentences consisting not at least of two words
            elif len(sentence.metadata["text"].split(" "))<=1:
                print("\t\t Sentence text,", sentence.metadata["text"], ", is too short.", infile, "skipping article nr", i)
                continue
            # delete sentences with autonodes and with no root
            f1=0; f2=1
            for token in sentence:
                if token["head"] == token["id"]:
                    f1= 1
                if token["head"] ==0:
                    f2 = 0
            if f1 or f2:
                if printf:
                    print("\t\tsentence with autonode or no root deleted in ", infile, "article nr", i, "nr", num)
                continue
            else:
                pass
            #print(article["custom_id"]+"_"+sentence.metadata["sent_id"].zfill(3))
            #adding some metadata, making sent number coherent in a colection of articles
            sentence.metadata.update({"sent_id":str(sent_id_counter).zfill(5),"article_id":article["custom_id"], "batch_id":article["batch_id"], "custom_sent_id":article["custom_id"]+"_"+sentence.metadata["sent_id"].zfill(3)})
            sentence.metadata.update({"filename":infile})
            sentence.metadata.update({"url":article["url"]})
            #print(sentence.metadata)
            macro_conllu_string= macro_conllu_string+sentence.serialize()
        if printf:
            print(f"\tarticle {i} took {time.time()-t1} seconds, {time.time()-t0}s so far")
    if printf:
        print(f"Spacy analysis of {len(article_list)} articles took {time.time()-t0} seconds in total", "\n***"*2)
    with open("analysed_corpus/"+outfile, "w") as file:
        file.write(macro_conllu_string)



def spacy_analysis_corpus(codi, llista_temes, model):
    # 1h
    # Spacy analysis begins
    done = []
    n_model = model
    corpus_list = []
    if isinstance(llista_temes, dict):
        llista = llista_temes.keys()
    elif isinstance(llista_temes, list):
        llista = llista_temes
    else:
        raise TypeError("llista_temes must be a dictionary or a list!")

    for tema in llista:
        if not glob.glob(f"data/{codi}tv3_corpus_*_{tema}.json"):
            raise Exception(f"File for topic {codi}tv3_corpus_*_{tema}.json not found.")
        elif len(glob.glob(f"data/{codi}tv3_corpus_*_{tema}.json")) > 0:
            glob.glob(f"data/{codi}tv3_corpus_*_{tema}.json").sort(reverse=True)
            corpuspath = glob.glob(f"data/{codi}tv3_corpus_*_{tema}.json")[0]
            corpusfile = corpuspath.split("/")[-1]

        if not glob.glob(f"data/{codi}KI_corpus_*_{tema}_{n_model}.json"):
            raise Exception(f"File for topic {codi}KI_corpus_*_{tema}_{n_model}.json not found.")
        elif len(glob.glob(f"data/{codi}KI_corpus_*_{tema}_{n_model}.json")) > 0:

            glob.glob(f"data/{codi}KI_corpus_*_{tema}_{n_model}.json").sort(reverse=True)
            KIpath = glob.glob(f"data/{codi}KI_corpus_*_{tema}_{n_model}.json")[0]
            KIfile = KIpath.split("/")[-1]

        corpus_list.append(KIfile)
        corpus_list.append(corpusfile)

    for infile in corpus_list:
        outfile = infile.replace(".json", ".conllu")
        try:
            spacy_pipeline(infile, outfile)
            done.append(outfile)
            print("Spacy analysis printed to", outfile)
            print("\t files analysed so far:", done)
        except Exception as e:
            print("ERROR", e)

