import os
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

docs      = []
doc_names = []

path = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_base")
path = os.path.abspath(path)

for file in sorted(os.listdir(path)):
    if file.endswith(".txt"):
        with open(os.path.join(path, file), "r", encoding="utf-8") as f:
            content = f.read()
            docs.append(content)
            doc_names.append(file.replace(".txt", ""))

embeddings = model.encode(docs)
index      = faiss.IndexFlatL2(384)
index.add(embeddings)


def retrieve(query: str, k: int = 2) -> dict:
    """
    Returns {
      "context": combined text of top-k chunks,
      "sources": list of source names,
      "chunks":  list of {"source": ..., "text": ...}
    }
    """
    q        = model.encode([query])
    D, I     = index.search(q, k=k)
    chunks   = []
    sources  = []

    for idx in I[0]:
        if 0 <= idx < len(docs):
            chunks.append({"source": doc_names[idx], "text": docs[idx]})
            sources.append(doc_names[idx])

    context = "\n\n---\n\n".join(c["text"] for c in chunks)
    return {"context": context, "sources": sources, "chunks": chunks}