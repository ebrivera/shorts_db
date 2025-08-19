from sentence_transformers import SentenceTransformer
import numpy as np


# set the model if we have one we want to particularly yse
_model = None

def get_model():
    global _model
    if _model is None:
        # otherwise we use the default model
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model


def embed_text(title: str, description: str, tags: list[str]) -> np.ndarray:
    # this is going to add a title (if one exists), tags (if any), and the first 512 characters of the description
    text = (title or "") + "\n" + " ".join(tags or []) + "\n" + (description or "")[:512]
    vec = get_model().encode([text], normalize_embeddings=True)[0]
    return vec.astype("float32")

