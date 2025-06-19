#!/usr/bin/env python

#analitza text en catala fent servir l spacy i el guarda en format conllu
#aquest funcio es pot executar de la manera seguent :D

import sys

def spacy_to_conll(text):
    import spacy
    import spacy_conll
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
    #content=content.lower()
    return content


def main():
    with open("deanotate/d50_ca_ancora-ud-train.conllu.txt", "r") as file:
        content = file.read()
    content = clean_text(content)

    with open("50_ca_spacy.conllu", "w") as f:
        f.write(spacy_to_conll(content))



if __name__ == "__main__":
    main()

