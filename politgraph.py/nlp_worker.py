import spacy
from spacy import language

def load_nlp() -> language:
    return spacy.load("de_core_news_sm", disable=["tagger", "parser", "ner", "textcat"])
