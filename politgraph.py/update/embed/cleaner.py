import asyncio
from typing import Any, Dict, List, Tuple

from tqdm.auto import tqdm
from update.extract.dtos import MemberDTO, AffairDTO

from bs4 import BeautifulSoup
import html as ihtml
from spacy import language
from nltk.tokenize import sent_tokenize, word_tokenize
from gensim.models.doc2vec import TaggedDocument

class Cleaner:

    def __init__(self, *, nlp:language):
        self._nlp = nlp

    async def clean_documents(self, *, docs: List[Tuple[MemberDTO, AffairDTO]], concurrency: int = 10) -> None:
        sem = asyncio.Semaphore(concurrency)

        lock = asyncio.Lock()
        pbar = tqdm(total=len(docs), desc="Cleaning documents", unit="document")

        async def worker(doc: AffairDTO) -> None:
            await sem.acquire()
            try:
                text_clean = await self._clean(doc.text_raw)
                lemmas = await self.lemmatize(text_clean)
                doc.text_clean = text_clean
                doc.tagged_doc = TaggedDocument(lemmas, [doc.id,]) # d2v erwartet eine tag-liste
                doc.lemmas = ' '.join(lemmas)
            finally:
                sem.release()
                async with lock:
                    pbar.update(1)
        
        try:
            await asyncio.gather(*(worker(doc) for (_, doc) in docs))
        finally:
            pbar.close()
        
    
    async def _clean(self, text: str) -> str:
        text = ihtml.unescape(text)
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(" ", strip=True)

    async def lemmatize(self, text: str) -> list[str]:
        doc = self._nlp(text)
        return [t.lemma_ for t in doc if  
            not t.is_space and not t.is_stop and not t.is_punct]