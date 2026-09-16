
import json
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

class Retrieval:
    def __init__(self, data_path, index_path, metadata_path):
        self.pool = pd.read_csv(data_path, dtype={"conversation_id": str})
        self.index = faiss.read_index(str(index_path))

        with open(metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

        if len(self.pool) != self.index.ntotal:
            raise ValueError("Pool B and FAISS vector counts differ.")
        if len(self.metadata) != self.index.ntotal:
            raise ValueError("Metadata and FAISS vector counts differ.")

    def query(self, message, k=3):
        q = self.embedder.encode(
            [message],
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype("float32")

        scores, ids = self.index.search(q, k)
        out = []

        for score, idx in zip(scores[0], ids[0]):
            if idx < 0:
                continue

            row = self.pool.iloc[int(idx)]

            out.append({
                "conversation_id": str(row["conversation_id"]),
                "score": float(score),
                "customer_issue_text": str(row["customer_issue_text"]),
                "final_resolution_text": str(row["final_resolution_text"])
            })

        return out
