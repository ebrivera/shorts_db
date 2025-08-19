import faiss, sqlite3, numpy as np, json

from vectorizers.text import embed_text, get_model

def load_vectors(db_path: str = "youtube_shorts.db"):
    """
    This function is going to load the vectors from the database and return the index, ids, and matrix
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # this is going to get all the videos that are not tombstoned getting the id, title, description, and tags
    rows = conn.execute("SELECT id,title,description,tags FROM shorts WHERE tombstoned_at IS NULL").fetchall()
    ids, vecs = [], []

    for row in rows:
        tags = json.loads(row["tags"]) or []
        vecs.append(embed_text(row["title"], row["description"], tags))
        ids.append(row["id"])

    if not vecs:
        return None, [], None
    
    matrix = np.vstack(vecs).astype("float32")
    index = faiss.IndexFlatIP(matrix.shape[1])
    index.add(matrix)  # normalized ->inner product == cosine
    return index, ids, matrix


def embed_query(q: str) -> np.ndarray:
    """
    This function is purely creating a vector embedding of the query
    params:
        q: str - the query to embed
    returns:
        np.ndarray - the vector embedding of the query
    """
    vec = get_model().encode([q], normalize_embeddings=True)[0]
    return vec.astype("float32")

def search(q: str, top_k: int = 10):
    """
    This function is going to search the index for the top k results
    params:
        q: str - the query to search for
        top_k: int - the number of results to return
    returns:
        list[tuple[str, float]] - the top k results
    """
    idx, ids, _ = load_vectors()
    if not idx:
        return []
    query_vector = embed_query(q) # using custom embedding function
    scores, indices = idx.search(query_vector.reshape(1, -1), top_k)
    return [(ids[i], scores[0][j]) for j, i in enumerate(indices[0]) if i != -1]


if __name__ == "__main__":
    print(search("python3 tutorials"))