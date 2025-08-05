#!/usr/bin/env python

#analitza text en catala fent servir l spacy i el guarda en format conllu
#aquest funcio es pot executar de la manera seguent :D
# ./spacy_to_conll text.txt > prova_conll.conllu -> ja no,  me n he cansat

import os
import sys

def spacy_to_conll(text, lang= "ca"):
    import spacy
    import spacy_conll
    if lang == "ca":
        nlp = spacy.load("ca_core_news_trf")
    nlp.add_pipe("conll_formatter",config={"include_headers": True}, last=True)
    doc = nlp(text)

    return doc._.conll_str

# neteja el text per ajudar l spacy a trobar coses
def clean_text(content):
    if content == None:
        return None
    list_of_problematic_characters = ["\r", "\t", '"', "“"]
    for c in list_of_problematic_characters:
        content = content.replace(c, "")
    content = content.replace("”", ".")
    content = content.replace("\n", " ")
    content = content.replace("  ", " ")
    #content = content.replace("pta.", "pta") # carregar me abreviatures que poden carregar-se el separador de frases de l spacy
    #content = content.lower()
    return content


def main(infile, outfile, lang= "ca"):
    infolder = "sentences"
    outfolder = "analysis"
    os.makedirs(infolder, exist_ok=True)
    os.makedirs(outfolder, exist_ok=True)

    with open(os.path.join(infolder, infile), "r") as file:
        content = file.read()
    content = clean_text(content)

    with open(os.path.join(outfolder, outfile), "w") as f:
        f.write(spacy_to_conll(content, lang))



if __name__ == "__main__":
    main()

