import json
import spacy
import os

import text_worker

import de_core_news_sm

nlp = de_core_news_sm.load(disable=["tagger", "parser", "ner", "textcat"])

appdata = os.getenv("APPDATA")
path = os.path.join(appdata, "politgraph", "members.json")

if not os.path.exists(path):
    raise FileNotFoundError(f"Die Datei {path} wurde nicht gefunden.")

with open (path, 'r') as f:
    members = json.load(f)


for memberId, member in members.items():
    for affair in member["Affairs"]:
        cleanText = text_worker.clean(affair["TextRaw"])
        lemmas = text_worker.lemmatize(cleanText, nlp)
        affair["Lemmas"] = lemmas

with open (path, 'w') as f:
    json.dump(members, f, indent=3)