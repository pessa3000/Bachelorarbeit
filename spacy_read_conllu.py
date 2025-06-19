import spacy

from spacy_conll import init_parser
from spacy_conll.parser import ConllParser

#nlp = spacy.load("ca_core_news_sm")
#nlp.add_pipe("conll_formatter", last=True)
nlp = ConllParser(init_parser("ca_core_news_sm", "spacy"))

doc = nlp.parse_conll_file_as_spacy("prova_conll.conllu")
"""conllstr = 
# text = From the AP comes this story :
1	From	from	ADP	IN	_	3	case	3:case	_
2	the	the	DET	DT	Definite=Def|PronType=Art	3	det	3:det	_
3	AP	AP	PROPN	NNP	Number=Sing	4	obl	4:obl:from	_
4	comes	come	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	0	root	0:root	_
5	this	this	DET	DT	Number=Sing|PronType=Dem	6	det	6:det	_
6	story	story	NOUN	NN	Number=Sing	4	nsubj	4:nsubj	_
"""

# Multiple CoNLL entries (separated by two newlines) will be included as different sentences in the resulting Doc
for sent in doc.sents:
    for token in sent:
        print(token.text, token.dep_, token.pos_)
