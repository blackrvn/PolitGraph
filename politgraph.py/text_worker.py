# Von ChatGPT 5.2 am 20.01.2026 generiert

from bs4 import BeautifulSoup
import html as ihtml
from spacy import language


def clean(text: str) -> str:
    text = ihtml.unescape(text)
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(" ", strip=True)

def lemmatize(text: str, nlp:language) -> list[str]:
    text = clean(text)
    doc = nlp(text)
    return [t.lemma_ for t in doc if  
            not t.is_space and not t.is_stop and not t.is_punct]