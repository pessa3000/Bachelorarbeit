import html
import emoji
import re
from fast_langdetect import detect



def gen_r2c(text):
    # html_text = html_text.replace(".&amp;nbsp;", ".\n")
    if not text:
        return
    # the text will be html.unescaped at the end again
    text = html.unescape(html.unescape(text))
    # removing tabs
    list_of_problematic_characters = ["\r", "\t"]
    for c in list_of_problematic_characters:
        text = text.replace(c, "")
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
            for i in range(4):
                if len(par) < i:
                    break
                if par.strip()[-i] == character:
                    # print(line, "removed")
                    flag = 1
                    break
        if flag == 1:
            continue
        # removing titles
        if par.strip()[-1].isalnum():
            continue

        # remove emojis
        if emoji.emoji_count(par) > 0:
            # print("\t emoji found :)", emoji.emoji_list(line))
            continue
        # remove urls
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        if url_pattern.search(par):
            #print("found url")
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
    if not text:
        return text

    # critical signs of "AI talking to itself"
    if "Gràcies!" in text:
        return ""
    clean_text1 = ""
    for par in text.split("\n"):
        if not par:
            continue
        #removing KI enumerations, also titles
        if par.strip()[0] == "*":
            # print("3skipped '", paragraph, "'")
            continue

        if not clean_text1:
            clean_text1 = par
            continue
        else:
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

    # removing AI problematic characters, text
    problematic_chars = [ "[", "]", "/", "*", "?", "EFE", "ACN", "El Punt Avui", "Vilaweb", "preguntes:"]
    for sentence in cleaned_text.split(". "):
        if bool("(" in sentence) ^ bool(")" in sentence):
            print("uncomplete parenthesis found: ", sentence)
            continue
        flag = 0
        for char in problematic_chars:
            if sentence.find(char) != -1:
                flag = 1
                break
        if flag == 1:
            print(f"\t {char} found in sentence: {sentence}, skipping")
            continue
        # check if there s an alphabetic char in the sentence
        flag = 1
        for character in sentence:
            if character.isalpha():
                flag = 0
                break
        if flag == 1:
            print(f"\t Deleting non-text sentence: {sentence}")
            continue

    # check if there s a colon. delete everything after the last colon
    if cleaned_text.find(".") == -1:
        print("err, no colon in the whole KI text")
        return ""
    else:
        cleaned_text = cleaned_text[:cleaned_text.rindex(".")] + "."
    return cleaned_text

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
        text= cleaned_text1
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
                continue
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


def tv3_r2c(text):
    # tv3 specific stuff to remove
    # enumerations
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
    data_pars = ""
    for par in text.split("\n"):
        # remove enumerations
        # tv3 style:
        if par[0] in ["-"]:
            # print("remove", line)
            continue
        # KI style:

        if not data_pars:
            data_pars = par
            continue
        else:
            data_pars = data_pars + "\n" + par


    # eliminating paragraphs
    data_text= data_pars.replace("\n", " ")
    data_clean=""

    for i in range(10):
        data_text=data_text.replace("  ", " ")

    for sent in data_text.split(". "):
    # removing sentences w questions, exclamation marks, and : bc spacy can't handle them
        flag=0
        for char in [":", "!", "?"]:
            if char in sent:
                flag=1
        if flag==1:
            continue



        # adding sentences
        if not data_clean:
            data_clean = sent
        else:
            data_clean = data_clean + ". " + sent

    return data_clean
