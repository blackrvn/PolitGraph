import logging
import sys
from typing import List, Tuple
from tqdm.auto import tqdm
from update.extract.dtos import MemberDTO, AffairDTO
from bs4 import BeautifulSoup
import html as ihtml
from spacy import language
from gensim.models.doc2vec import TaggedDocument

logger = logging.getLogger(__name__)


class Cleaner:
    def __init__(self, *, nlp:language):
        self._nlp = nlp
    def clean_documents(self, *, docs: List[Tuple[MemberDTO, AffairDTO]], batch_size: int = 1000, pipe_batch_size: int = 64) -> None:
        pbar = tqdm(total=len(docs), desc="Cleaning documents", unit="document")
        empty = 0
        try:
            for start in range(0, len(docs), batch_size):
                batch = docs[start:start + batch_size]
                texts = [self._strip_html(doc.text_raw) for (_, doc) in batch]
                # memory_zone: Vocab/StringStore/Tokenizer-Cache-Einträge dieses Batches
                # werden beim Verlassen wieder freigegeben. Es dürfen keine spaCy-Objekte
                # (Doc/Token) den Block überleben — nur interned Python-Strings.
                with self._nlp.memory_zone():
                    for (member, doc), spacy_doc in zip(batch, self._nlp.pipe(texts, batch_size=pipe_batch_size)):
                        lemmas = [
                            sys.intern(t.lemma_) for t in spacy_doc
                            if not t.is_space
                            and not t.is_stop
                            and not t.is_punct
                            and not t.is_digit
                            and not t.like_num
                            and not t.like_url
                            and not t.like_email
                        ]
                        if not lemmas:
                            empty += 1
                        doc.tagged_doc = TaggedDocument(lemmas, [doc.id, member.id]) # d2v erwartet eine tag-liste
                        doc.text_raw = None
                        pbar.update(1)
                texts = None
                pbar.set_postfix(strings=len(self._nlp.vocab.strings), empty=empty, refresh=False)
        finally:
            pbar.close()
        logger.info(f"Cleaned {len(docs)} documents ({empty} produced no lemmas)")

    def _strip_html(self, text: str) -> str:
        text = ihtml.unescape(text)
        soup = BeautifulSoup(text, "html.parser")
        text = soup.get_text(" ", strip=True)
        if len(text) > self._nlp.max_length:
            text = text[:self._nlp.max_length]
        return text
