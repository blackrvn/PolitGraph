from typing import Any, Dict, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix

from update.extract.dtos import MemberDTO, AffairDTO
from update.embed.evaluator import Doc2VecConfig

from gensim.models.doc2vec import Doc2Vec
import numpy as np

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
        corpus = [doc.tagged_doc for (_, doc) in docs]
        self.model = Doc2Vec(**self.config.to_dict(), workers=self.workers)
        self.model.build_vocab(corpus)
        self.model.train(corpus, total_examples=self.model.corpus_count, epochs=self.model.epochs)
        for (_, doc) in docs:
            doc.w2v_vector = self.model.dv[doc.id]

    def embed_members(self, members: List[MemberDTO]):
        for member in members:
            member.w2v_vector = normalize(
                self.model.dv[member.id].reshape(1, -1)
            )



