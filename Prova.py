import spacy, os
from spacy.matcher import Matcher

from spacy.lang.ca.examples import sentences

#nlp = spacy.load("ca_core_news_sm")
nlp = spacy.load("ca_core_news_trf")

#llegir el text
with open("text.txt", "r") as file:
    content = file.read()
doc = nlp(content)

# content= content.replace(".", ".\n")
# with open("text.txt", "w") as file:
#     file.write(content)
# print(content, "\n")

pattern_nadj = [{"POS":"NOUN"}, {"POS":"ADJ"}]
    
def pattern_counter(text, pattern):
    matcher = Matcher(nlp.vocab)
    matcher.add("string", [pattern])
    matches = matcher(text)
    #troba coses
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]
        span = text[start:end]
        print(match_id, string_id, start, end, span.text)
    return len(matches)


pattern1= [{"DEP":"NSUBJ"}]
pattern2= [{"MORPH":"Gender=Masc|Number=Plur"},{"MORPH":"Gender=Masc|Number=Plur"}]
#pattern_counter(doc, pattern1)

for token in doc:
    print(token.text, token.pos_, token.dep_, token.lemma_, token.head.dep_, token.morph)

