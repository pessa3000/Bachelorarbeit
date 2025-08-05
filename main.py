
from spacy_conllu import main as spacy_main
import spacy_pickle
import read_conllu
from read_conllu import test_annotation, test_annotation_poli, deanotate
from spacy_pickle import pickle_write, pickle_read


#deanotate("ca_ancora-ud-train.conllu", "ca_5_ancora.txt", 5)
spacy_main("KI_incendis.txt", "KI_incendis.conllu")

#file names: "ca_ancora-ud-train.conllu", "200_ca_spacy_low.conllu", "200_ca_spacy.conllu"
#pickle_write(test_annotation_poli("ca_ancora-ud-train.conllu", "200_ca_spacy.conllu", 200), "200_ca_spacy.pickle" )
#print(pickle_read("200_ca_spacy.pickle"))