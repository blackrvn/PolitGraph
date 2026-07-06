import logging
from typing import Any, Dict, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix

from update.extract.dtos import MemberDTO, AffairDTO
from update.embed.evaluator import Doc2VecConfig

from gensim.models.doc2vec import Doc2Vec
from gensim.models.callbacks import CallbackAny2Vec
from tqdm.auto import tqdm
import numpy as np

logger = logging.getLogger(__name__)


class _EpochProgress(CallbackAny2Vec):
    """tqdm-Fortschrittsbalken über die Trainings-Epochen von Doc2Vec."""

    def __init__(self, epochs: int, desc: str = "  Training Doc2Vec"):
        self._pbar = tqdm(total=epochs, desc=desc, unit="epoch", leave=False)

    def on_epoch_end(self, model: Doc2Vec) -> None:
        self._pbar.update(1)

    def on_train_end(self, model: Doc2Vec) -> None:
        self._pbar.close()

class TfIdfEmbedder:

    def __init__(self):
        self._vectorizer = TfidfVectorizer()

    def embed_documents(self, docs: List[Tuple[MemberDTO, AffairDTO]]):
        docs_to_embed = []
        self._member_indecies_map = {}
        for idx, (member, doc) in enumerate(docs):
            docs_to_embed.append(doc.lemmas)
            indecies = self._member_indecies_map.get(member, [])
            indecies.append(idx)
            self._member_indecies_map[member] = indecies
        
        sparse_matrix = self._vectorizer.fit_transform(docs_to_embed)
        svd = TruncatedSVD(n_components=256)
        truncated_matrix = svd.fit_transform(sparse_matrix)
        self._doc_embeddings = normalize(truncated_matrix)
        for idx, (_, doc) in enumerate(docs):
            doc.tfidf_vector = self._doc_embeddings[idx].reshape(1, -1)

    def embed_members(self):
        for member, indecies in self._member_indecies_map.items():
            submatrix = self._doc_embeddings[indecies]
            mean = submatrix.mean(axis=0) # (vector_size, )
            member.tfidf_vector = normalize(mean.reshape(1, -1)) # (1, vector_size)

class Doc2VecEmbedder:
    def __init__(self, config: Optional[Doc2VecConfig] = None, *, workers: int = 4):
        self.config = config or Doc2VecConfig()
        self.workers = workers

    def embed_documents(self, docs: List[Tuple[MemberDTO, AffairDTO]]):
        phases = tqdm(total=3, desc="Embedding", unit="phase", leave=False)

        phases.set_postfix_str("building vocab")
        corpus = [doc.tagged_doc for (_, doc) in docs]
        self.model = Doc2Vec(**self.config.to_dict(), workers=self.workers)
        self.model.build_vocab(corpus)
        logger.info(
            f"Doc2Vec vocab built: {len(corpus)} documents, "
            f"{len(self.model.wv)} terms ({self.config})"
        )
        phases.update(1)

        phases.set_postfix_str(f"training ({self.model.epochs} epochs)")
        self.model.train(
            corpus,
            total_examples=self.model.corpus_count,
            epochs=self.model.epochs,
            callbacks=[_EpochProgress(self.model.epochs)],
        )
        phases.update(1)

        phases.set_postfix_str("assigning doc vectors")
        for (_, doc) in tqdm(docs, desc="  Doc vectors", unit="doc", leave=False):
            doc.w2v_vector = self.model.dv[doc.id]
        phases.update(1)

        phases.close()
        logger.info(f"Embedded {len(docs)} documents")

    def embed_members(self, members: List[MemberDTO]):
        for member in tqdm(members, desc="  Member vectors", unit="member", leave=False):
            member.w2v_vector = normalize(
                self.model.dv[member.id].reshape(1, -1)
            )
        logger.info(f"Embedded {len(members)} members")



