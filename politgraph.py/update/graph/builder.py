from typing import List

from scipy.sparse import vstack

from update.extract.dtos import EdgeDTO, MemberDTO
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from numpy.linalg import norm

class EdgeBuilder:
    def __init__(self, *, 
                 n_neighbors:int = 5, 
                 metric: str = "cosine", 
                 algorithm: str = "brute",
                 threshold = 0.5):
        self._neighbors = n_neighbors
        self._metric = metric
        self._algorithm = algorithm
        self._threshold = threshold

    def calculate_neighbors_tfidf(self, *, members: List[MemberDTO]) -> List[EdgeDTO]:

        matrix = vstack([m.tfidf_vector for m in members]) 

        nn = NearestNeighbors(
            n_neighbors=self._neighbors + 1, # +1 wegen self-match
            metric=self._metric,
            algorithm=self._algorithm
            )
        nn.fit(matrix)
        dist, neighbors = nn.kneighbors(matrix, return_distance=True)
        edges = []
        for idx, kn in enumerate(neighbors):
            source_member = members[idx]
            for i in range(1, len(kn)): # kn[0] == self-match
                n = kn[i]
                target_member = members[n]
                sim = 1 - dist[idx][i] # 1 - Distanz = Ähnlichkeit 
                if sim >= self._threshold:
                    edge = EdgeDTO(source_member.id, target_member.id, sim)
                    edges.append(edge)

        return edges

    def calculate_neighbors_d2v(self, *, members: List[MemberDTO]) -> List[EdgeDTO]:

        matrix = np.vstack([m.w2v_vector for m in members]) 

        nn = NearestNeighbors(
            n_neighbors=self._neighbors + 1, # +1 wegen self-match
            metric=self._metric,
            algorithm=self._algorithm
            )
        nn.fit(matrix)
        dist, neighbors = nn.kneighbors(matrix, return_distance=True)
        edges = []
        for idx, kn in enumerate(neighbors):
            source_member = members[idx]
            for i in range(1, len(kn)): # kn[0] == self-match
                n = kn[i]
                target_member = members[n]
                sim = 1 - dist[idx][i] # 1 - Distanz = Ähnlichkeit 
                if sim >= self._threshold:
                    edge = EdgeDTO(source_member.id, target_member.id, sim)
                    edges.append(edge)

        return edges
        





