import os
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

docs = []
path = "data/knowledge_base"

for file in os.listdir(path):

    with open(os.path.join(path, file)) as f:
        docs.append(f.read())

embeddings = model.encode(docs)

index = faiss.IndexFlatL2(384)
index.add(embeddings)

faiss.write_index(index, "vectorstore/index.faiss")