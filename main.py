from spacy_conll import init_parser
from spacy_conll.parser import ConllParser

#nlp = init_parser("ca_core_news_sm",
 #                 "spacy",
  #                #ext_names={"conll_pd": "pandas"},
   #               #conversion_maps={"deprel": {"nsubj": "subj"}}
    #              )

nlp = ConllParser(init_parser("en_core_web_sm", "spacy"))
doc = nlp.parse_conll_file_as_spacy("prova_conll.conllu")
print(doc._.conll)