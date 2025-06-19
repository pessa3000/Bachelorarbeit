#!/usr/bin/env python


#aquest funcio es pot executar de la manera seguent :D
#./spacy_to_conll.py text.txt > prova_conll.conllu

import sys

def spacy_to_conll(text):
    import spacy
    import spacy_conll
    nlp = spacy.load("ca_core_news_sm")
    nlp.add_pipe("conll_formatter",config={"include_headers": True}, last=True)
    doc = nlp(text)

    print(doc._.conll_str)

def main():
    if len(sys.argv) != 2:
        raise ValueError(f"Usage: {sys.argv[0]} <filename>")
    # This will raise FileNotFoundError if file doesn't exist

    filename = sys.argv[1]

    with open(filename, 'r') as file:
        content = file.read()
    list_of_problematic_characters=["\r", "\t", '"', "“"]
    for c in list_of_problematic_characters:
        content=content.replace(c, "")
    content=content.replace( "”", ".")
    content = content.replace("\n", " ")
    content=content.lower()
    spacy_to_conll(content)

if __name__ == "__main__":
    main()

