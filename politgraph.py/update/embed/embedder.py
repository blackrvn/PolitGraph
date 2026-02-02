from typing import Any, Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix

from update.extract.dtos import MemberDTO, AffairDTO

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

    def __init__(self, *, vector_size: int = 256, window: int = 5, min_count:int = 2, workers:int = 4, epochs:int=40):
        self.vector_size = vector_size
        self.window = window
        self.min_count = min_count
        self.workers = workers
        self.epochs = epochs

    def embed_documents(self, docs: List[Tuple[MemberDTO, AffairDTO]]):
        corpus = []
        self.member_map = {}
        for (member, doc) in docs:
            member_docs = self.member_map.get(member, [])
            member_docs.append(doc)
            corpus.append(doc.tagged_doc)
            self.member_map[member] = member_docs

        self.model = Doc2Vec(vector_size=self.vector_size, 
                            window=self.window,
                            min_count=self.min_count, 
                            workers=self.workers,
                            epochs=self.epochs)
        self.model.build_vocab(corpus)
        self.model.train(corpus, total_examples=self.model.corpus_count, epochs=self.model.epochs)
        for (_, doc) in docs:
            vector = self.model.dv[doc.id]
            doc.w2v_vector = vector

    def embed_members(self):
        for member, docs in self.member_map.items():
            vectors = []
            for doc in docs:
                vector = doc.w2v_vector
                if vector is not None:
                    v = np.asarray(doc.w2v_vector, dtype=np.float32)
                    vectors.append(v)

            mat = np.vstack(vectors) # (n_docs, vector_size)
            mean = mat.mean(axis=0) # (vector_size, )
            member.w2v_vector = normalize(mean.reshape(1, -1)) # (1, vector_size)



