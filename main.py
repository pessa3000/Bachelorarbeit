
from scraper.spacy_conllu import main as spacy_main

#deanotate("ca_ancora-ud-train.conllu", "ca_5_ancora.txt", 5)
spacy_main("tv3_salut.txt", "tv3_salut.conllu")

#file names: "ca_ancora-ud-train.conllu", "200_ca_spacy_low.conllu", "200_ca_spacy.conllu"
#pickle_write(test_annotation_poli("ca_ancora-ud-train.conllu", "200_ca_spacy.conllu", 200), "200_ca_spacy.pickle" )
#print(pickle_read("200_ca_spacy.pickle"))