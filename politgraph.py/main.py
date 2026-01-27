# tqdm wurde durch ChatGPT am 25.01.2026 integriert.

import json
import spacy
import os
import sys

from tqdm import tqdm

import text_worker
import de_core_news_sm


# argv[0] = script name
if len(sys.argv) > 2:
    raise SyntaxError("Use either 0 or 1 argument")

memberId = None
if len(sys.argv) == 2:
    try:
        memberId = int(sys.argv[1])
    except ValueError:
        raise ValueError("The argument must be an int")


nlp = de_core_news_sm.load(disable=["tagger", "parser", "ner", "textcat"])


appdata = os.getenv("APPDATA")
path = os.path.join(appdata, "politgraph", "members.json")

if not os.path.exists(path):
    raise FileNotFoundError(f"The file {path} was not found")

with open(path, "r", encoding="utf-8") as f:
    members = json.load(f)


def update_member(mid: int, member_obj: dict):
    affairs = member_obj.get("Affairs", [])
    for affair in tqdm(affairs, desc=f"Cleaning texts for member {mid} - {member_obj["Name"]}", leave=False):
        text_raw = affair.get("TextRaw")
        cleanText = text_worker.clean(text_raw)
        lemmas = text_worker.lemmatize(cleanText, nlp)
        affair["Lemmas"] = lemmas


# Einen / alle Member updaten
if memberId is not None:
    key = str(memberId)
    if key not in members:
        raise KeyError(f"MemberId {memberId} not found in {path}")
    update_member(memberId, members[key])
else:
    for mid_str, member in tqdm(members.items(), desc="Cleaning texts for every member"):
        update_member(int(mid_str), member)


with open(path, "w", encoding="utf-8") as f:
    json.dump(members, f, indent=3, ensure_ascii=False)
