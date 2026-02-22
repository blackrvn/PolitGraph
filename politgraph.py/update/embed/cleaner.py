import asyncio
from typing import List, Tuple
from tqdm.auto import tqdm
from update.extract.dtos import MemberDTO, AffairDTO
from bs4 import BeautifulSoup
import html as ihtml
from spacy import language
from gensim.models.doc2vec import TaggedDocument
from gensim.models.phrases import Phrases
import logging

logger = logging.getLogger(__name__)

class Cleaner:
    # Wörter zur Erkennung von Phrasen
    DE_CONNECTOR_WORDS = frozenset({
        "der", "die", "das", "des", "dem", "den",
        "ein", "eine", "eines", "einem", "einen", "einer",
        "und", "oder", "für", "von", "vom", "zur", "zum",
        "mit", "auf", "in", "im", "an", "am",
    })

    def __init__(self, *, nlp: language):
        self._nlp = nlp
        self._phraser = None

    async def clean_documents(
        self,
        *,
        docs: List[Tuple[MemberDTO, AffairDTO]],
        concurrency: int = 10,
        bigram_min_count: int = 10,
        bigram_threshold: float = 15.0,
    ) -> None:
        sem = asyncio.Semaphore(concurrency)
        lock = asyncio.Lock()

        # Clean / Lemmatize
        pbar = tqdm(total=len(docs), desc="Phase 1/3: Cleaning + Lemmatizing", unit="doc")
        lemma_cache: dict = {}

        async def clean_worker(member_id: int, doc: AffairDTO) -> None:
            await sem.acquire()
            try:
                text_clean = await self._clean(doc.text_raw)
                lemmas = await self.lemmatize(text_clean)
                doc.text_clean = text_clean
                lemma_cache[(member_id, doc.id)] = lemmas
            finally:
                sem.release()
                async with lock:
                    pbar.update(1)

        try:
            await asyncio.gather(*(clean_worker(member.id, doc) for (member, doc) in docs))
        finally:
            pbar.close()

        # Phrase Detection trainieren
        logger.info("Phase 2/3: Training bigram phraser")
        all_lemmas = list(lemma_cache.values())
        phrases_model = Phrases(
            tqdm(all_lemmas, desc="Phase 2/3: Training phraser", unit="doc"),
            min_count=bigram_min_count,
            threshold=bigram_threshold,
            connector_words=self.DE_CONNECTOR_WORDS,
        )
        self._phraser = phrases_model.freeze()

        export = list(phrases_model.export_phrases().keys())[:15]
        logger.info(f"Phraser trained, {len(export)} example phrases: {export}")

        # TaggedDocument mit Phrasen erstellen
        pbar = tqdm(total=len(docs), desc="Phase 3/3: Applying phrases", unit="doc")
        for (member, doc) in docs:
            lemmas = lemma_cache[(member.id, doc.id)]
            phrased = list(self._phraser[lemmas])
            doc.tagged_doc = TaggedDocument(phrased, [doc.id, member.id])
            doc.lemmas = " ".join(phrased)
            pbar.update(1)
        pbar.close()

    async def _clean(self, text: str) -> str:
        text = ihtml.unescape(text)
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(" ", strip=True)

    async def lemmatize(self, text: str) -> list[str]:
        doc = self._nlp(text)
        return [t.lemma_ for t in doc if
                not t.is_space and 
                not t.is_stop and 
                not t.is_punct and 
                not t.is_digit]