import io
import numpy as np
from scipy.sparse import csr_matrix

def csr_to_blob(m: csr_matrix) -> bytes:
    bio = io.BytesIO()

    data = np.asarray(m.data, dtype=np.float32)
    indices = np.asarray(m.indices, dtype=np.int32)
    indptr = np.asarray(m.indptr, dtype=np.int32)
    shape = np.asarray(m.shape, dtype=np.int64)
    np.savez_compressed(bio, data=data, indices=indices, indptr=indptr, shape=shape)
    return bio.getvalue()


def blob_to_csr(blob: bytes) -> csr_matrix:
    bio = io.BytesIO(blob)
    loader = np.load(bio, allow_pickle=False)
    shape = tuple(loader["shape"])
    return csr_matrix((loader["data"], loader["indices"], loader["indptr"]), shape=shape)


