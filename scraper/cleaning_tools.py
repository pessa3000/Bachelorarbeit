import html


import emoji
import re
from fast_langdetect import detect



def gen_r2c(text):
    # html_text = html_text.replace(".&amp;nbsp;", ".\n")
    if not text:
        print("\tgen_r2c: no text")
        return

    # the text will be html.unescaped at the end again
    text = html.unescape(html.unescape(text))
    # removing tabs
    list_of_problematic_characters = ["\r", "\t"]
    for c in list_of_problematic_characters:
        text = text.replace(c, "")
    text = text.replace("\xa0", " ")
    # not necessary:
    # html_text = html_text.replace("&nbsp;", " ")
    # html_text = html_text.replace("\u00a0", " ")
    # for i in range(6):
    #    html_text= html_text.replace("\n\n", "\n")
    clean_text1 = ""
    j = 0
    for par in text.split("\n"):
        j += 1
        # print(j, line)
        # remove empty lines
        if not par:
            continue
        if len(par) < 2 or par.isspace():
            continue
        # AI texts use this to separate the "news text" from their reflections, answers, etc
        if "---" in par:
            break
        # if string in paragraph, paragraph gets removed
        # anything suspicious of being a tweet
        bad_strings = ["function", ".twitter", "&#", "@", "&", "¿", "¡", "#", "(···)", "(...)"]
        flag = 0
        for s in bad_strings:
            if s in par:
                flag = 1
                break
        if flag == 1:
            continue
        # If paragraph ends in these characters, i remove the whole paragraph
        # removing citation blocks, titles and picture captions
        bad_characters = ['"', "“", "”", ")"]
        flag = 0
        for character in bad_characters:
            if par.strip()[-1] == character:
                #print(f"\tgen_r2c: char {character} in paragraph end", par, "removed")
                flag = 1
                break
        if flag == 1:
            continue
        # removing titles and unfinished AI sentences
        if par.strip()[-1].isalnum():
            # print("\tgen_r2c: removing title", par)
            continue

        # remove emojis
        if emoji.emoji_count(par) > 0:
            # print("\t gen_r2c emoji found :)", emoji.emoji_list(par))
            continue
        # remove urls
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        if url_pattern.search(par):
            # print("\tgen_r2c: found url")
            continue

        # filtering other languages
        if detect(par, model='lite', k=1)[0]["lang"] == "ca":
            flag = 0
        else:
            flag = 1
            for guess in detect(par, model='full', k=3):
                if "ca" == guess["lang"] and guess["score"] > 0.1:
                    #print("suspicious but catalan", sentence)
                    # print(guess)
                    flag = 0
                    #print("\t low confidence catalan paragraph", par)
                    break
                else:
                    pass
            # print("eing", sentence)
        if flag == 1:
            print("\t removing non catalan sentence:'", par, "'")
            # print(detect(sentence, model='lite', k=3))
            continue


        # adding the surviving paragraphs
        if not clean_text1:
            clean_text1 = par
            continue
        else:
            clean_text1 = clean_text1 + "\n" + par

    # PARAGRAPHS ARE PRESERVED
    return clean_text1

# KI specific cleaning
def KI_r2c(text):
    print("ENTERING KI_r2c")
    if not text:
        return text

    if text.strip()[-1] != ".":
        print("\tKI_r2c: deleting last unfinished sentence", text.split(".")[-1])
        if ". " in text:
            text = text[:text.rindex(". ")] + ". "
        else:
            return

    clean_text1 = ""
    for par in text.split("\n"):
        if not par:
            continue
        #print("par", par)
        #removing KI enumerations, also titles

        # critical signs of "AI talking to itself" -> stop adding text
        self_talk_words= ["De res.", "Sí, és cert.", "eniu raó", "ens raó","Perfecte!", "e res!", "Estic d'acord", "Sóc d'acord", "És cert", "Totalment cert",   "Molt ben dit", "Ho faré", "Exacte.", "Certament.", "Gràcies", "Absolutament.", "Perfecte.", "necessitaràs ampliar", " Moltes gràcies", "Moltíssimes gràcies", "otalment d'acord."]
        talking_to_user = ["spero que", " podeu ", "Si voleu ", " pots ", "Si vols", "Aquí teniu", "Si necessites", " dubtis"]
        critical_words = self_talk_words + talking_to_user

        flag=0
        for word in critical_words:
            if word in par:
                print(word, "in paragraph", par)
                flag=1
                break
        if flag == 1:
            break

        if not clean_text1:
            clean_text1 = par
            continue
        else:
            #print("adding", par)
            clean_text1 = clean_text1 + "\n" + par

    # delete text between the even "**" positions, as they are problematic
    pieces = clean_text1.split("**")
    if len(pieces) == 1:
        cleaned_text = pieces[0]
    else:
        cleaned_text = ""
        for i, piece in enumerate(pieces):
            if i % 2 == 0:
                cleaned_text = cleaned_text + piece
    print("\tKI_r2c survived from the ** cleaning: ",cleaned_text)
    cleaned_text = cleaned_text.replace("\n", " ")
    while "  " in cleaned_text:
        cleaned_text = cleaned_text.replace("  ", " ")
    # removing AI problematic characters, text
    problematic_chars = [ "[", "]", "/", "*"]
    clean_text1= ""

    for sentence in cleaned_text.split(". "):

        if bool("(" in sentence) ^ bool(")" in sentence):
            print("\t KI_r2c uncomplete parenthesis found: ", sentence)
            continue
        flag = 0
        for char in problematic_chars:
            if sentence.find(char) != -1:
                print("\t KI_r2c found '", char, "' in", sentence)
                flag = 1
                break
        if flag == 1:
            print(f"\t KI_r2c {char} found in sentence: {sentence}, skipping")
            continue
        # check if there s an alphabetic char in the sentence
        flag = 1
        for character in sentence:
            if character.isalpha():
                flag = 0
                break
        if flag == 1:
            print(f"\t KI_r2c Deleting non-text sentence: {sentence}")
            continue
        if not clean_text1:
            clean_text1 = sentence + ". "
            continue
        else:
            clean_text1 = clean_text1 + ". " + sentence


    while ". ." in clean_text1 or "  " in clean_text1:
        clean_text1 = clean_text1.replace(". . ", ". ")
        clean_text1 = clean_text1.replace("  ", " ")
    return clean_text1



def tv3_r2c(text):
    # tv3 specific stuff to remove
    # enumerations
    if not text:
        return text
    clean_pars=""
    for par in text.split("\n"):
        # remove enumerations
        # tv3 style:
        if not par:
            continue
        if par[0] in ["-"]:
            # print("remove", line)
            continue
        if not clean_pars:
            clean_pars = par
            continue
        else:
            clean_pars = clean_pars + "\n" + par

    return clean_pars






def corpus_to_data(text):
    # paragraph cleaning
    # not needed since there are no paragraphs on arrival
    if not text:
        return text
    data_pars = ""
    for par in text.split("\n"):
        if not par:
            continue
        if not data_pars:
            data_pars = par
            continue
        else:
            data_pars = data_pars + "\n" + par


    # eliminating paragraphs
    data_text= data_pars.replace("\n", " ")



    data_clean=""

    for sent in data_text.split(". "):
        # removing sentences w questions, exclamation marks, and : bc spacy can't handle them
        for char in ["!"]:
            if sent.find(char) != -1:
                sent = sent[sent.rindex(char)+1:].strip()
        flag=0
        for char in [":", "?"]:
            if sent.find(char) != -1:
                flag=1
                break
        if flag==1:
            continue

        flag=1
        for char in sent:
            if char.isalpha():
                flag=0
                break
        if flag == 1:
            continue

        # adding sentences
        if not data_clean:
            data_clean = sent + ". "
        else:
            data_clean = data_clean + ". " + sent

    while "  " in data_clean or ". ." in data_clean:
        data_clean = data_clean.replace("  ", " ")
        data_clean = data_clean.replace(". .", ". ")
    if data_clean:
        #assegurar q l ultima frase acaba en punt
        if data_clean.strip()[-1] != ".":
            if len(data_clean) > 4:
                if "." not in data_clean[-3:]:
                    data_clean = data_clean + "."

    return data_clean
