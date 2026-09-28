# import os
# import glob
# import pickle

# import faiss
# import numpy as np
# from sentence_transformers import SentenceTransformer


# # --------------------------------------------------
# # Configuration
# # --------------------------------------------------

# KNOWLEDGE_DIR = "data/knowledge"
# INDEX_PATH = "data/faiss.index"
# DOCUMENTS_PATH = "data/documents.pkl"

# MODEL_NAME = "all-MiniLM-L6-v2"


# # --------------------------------------------------
# # Load embedding model
# # --------------------------------------------------

# model = SentenceTransformer(MODEL_NAME)


# # --------------------------------------------------
# # Load knowledge documents
# # --------------------------------------------------

# def load_documents():
#     """
#     Read all Markdown knowledge documents.
#     """

#     documents = []

#     files = glob.glob(
#         os.path.join(KNOWLEDGE_DIR, "*.md")
#     )

#     for file_path in files:

#         with open(
#             file_path,
#             "r",
#             encoding="utf-8"
#         ) as file:

#             content = file.read()

#         documents.append({
#             "source": os.path.basename(file_path),
#             "content": content
#         })

#     return documents


# # --------------------------------------------------
# # Create FAISS index
# # --------------------------------------------------

# def create_index():

#     documents = load_documents()

#     if not documents:
#         raise ValueError(
#             "No knowledge documents found."
#         )

#     texts = [
#         document["content"]
#         for document in documents
#     ]

#     print(
#         f"Creating embeddings for "
#         f"{len(texts)} documents..."
#     )

#     embeddings = model.encode(
#         texts,
#         convert_to_numpy=True
#     )

#     # Normalize embeddings
#     faiss.normalize_L2(embeddings)

#     dimension = embeddings.shape[1]

#     index = faiss.IndexFlatIP(dimension)

#     index.add(embeddings)

#     faiss.write_index(
#         index,
#         INDEX_PATH
#     )

#     with open(
#         DOCUMENTS_PATH,
#         "wb"
#     ) as file:

#         pickle.dump(
#             documents,
#             file
#         )

#     print("FAISS index created successfully.")

#     return index, documents


# # --------------------------------------------------
# # Load existing FAISS index
# # --------------------------------------------------

# def load_index():

#     if (
#         not os.path.exists(INDEX_PATH)
#         or not os.path.exists(DOCUMENTS_PATH)
#     ):
#         return create_index()

#     index = faiss.read_index(
#         INDEX_PATH
#     )

#     with open(
#         DOCUMENTS_PATH,
#         "rb"
#     ) as file:

#         documents = pickle.load(file)

#     return index, documents


# # --------------------------------------------------
# # Semantic search
# # --------------------------------------------------

# def search_knowledge(
#     query,
#     top_k=3
# ):

#     index, documents = load_index()

#     query_embedding = model.encode(
#         [query],
#         convert_to_numpy=True
#     )

#     faiss.normalize_L2(
#         query_embedding
#     )

#     scores, indices = index.search(
#         query_embedding,
#         top_k
#     )

#     results = []

#     for score, index_id in zip(
#         scores[0],
#         indices[0]
#     ):

#         if index_id == -1:
#             continue

#         document = documents[index_id]

#         results.append({
#             "source": document["source"],
#             "content": document["content"],
#             "score": float(score)
#         })

#     return results


# # --------------------------------------------------
# # Test
# # --------------------------------------------------

# if __name__ == "__main__":

#     results = search_knowledge(
#         "Database connection is taking too long and timing out"
#     )

#     for result in results:

#         print("\n-------------------------")

#         print(
#             f"Source: {result['source']}"
#         )

#         print(
#             f"Similarity: {result['score']:.4f}"
#         )

#         print(
#             result["content"][:500]
#         )


import os
import glob
import pickle

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


KNOWLEDGE_DIR = "data/knowledge"
INCIDENT_DIR = "data/incidents"

INDEX_PATH = "data/faiss.index"
DOCUMENTS_PATH = "data/documents.pkl"

INCIDENT_INDEX_PATH = "data/incidents.index"
INCIDENT_DOCUMENTS_PATH = "data/incidents.pkl"

MODEL_NAME = "all-MiniLM-L6-v2"


model = SentenceTransformer(MODEL_NAME)


# ============================================================
# KNOWLEDGE BASE
# ============================================================

def load_documents():
    documents = []

    files = glob.glob(
        os.path.join(KNOWLEDGE_DIR, "*.md")
    )

    for file_path in files:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read()

        documents.append({
            "source": os.path.basename(file_path),
            "content": content
        })

    return documents


def create_index():

    documents = load_documents()

    if not documents:
        raise ValueError(
            "No knowledge documents found."
        )

    texts = [
        document["content"]
        for document in documents
    ]

    print(
        f"Creating embeddings for {len(texts)} documents..."
    )

    embeddings = model.encode(
        texts,
        convert_to_numpy=True
    )

    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(embeddings)

    faiss.write_index(
        index,
        INDEX_PATH
    )

    with open(
        DOCUMENTS_PATH,
        "wb"
    ) as file:

        pickle.dump(
            documents,
            file
        )

    print(
        "FAISS knowledge index created successfully."
    )

    return index, documents


def load_index():

    if (
        not os.path.exists(INDEX_PATH)
        or not os.path.exists(DOCUMENTS_PATH)
    ):
        return create_index()

    index = faiss.read_index(
        INDEX_PATH
    )

    with open(
        DOCUMENTS_PATH,
        "rb"
    ) as file:

        documents = pickle.load(file)

    return index, documents


def search_knowledge(
    query,
    top_k=3
):

    index, documents = load_index()

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    )

    faiss.normalize_L2(
        query_embedding
    )

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, index_id in zip(
        scores[0],
        indices[0]
    ):

        if index_id == -1:
            continue

        document = documents[index_id]

        results.append({
            "source": document["source"],
            "content": document["content"],
            "score": float(score)
        })

    return results


# ============================================================
# HISTORICAL INCIDENTS
# ============================================================

def load_historical_incidents():

    incidents = []

    files = glob.glob(
        os.path.join(
            INCIDENT_DIR,
            "*.md"
        )
    )

    for file_path in files:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read()

        incidents.append({
            "source": os.path.basename(file_path),
            "content": content
        })

    return incidents


def create_incident_index():

    incidents = load_historical_incidents()

    if not incidents:
        raise ValueError(
            "No historical incidents found."
        )

    texts = [
        incident["content"]
        for incident in incidents
    ]

    print(
        f"Creating incident embeddings for {len(texts)} incidents..."
    )

    embeddings = model.encode(
        texts,
        convert_to_numpy=True
    )

    faiss.normalize_L2(
        embeddings
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(embeddings)

    faiss.write_index(
        index,
        INCIDENT_INDEX_PATH
    )

    with open(
        INCIDENT_DOCUMENTS_PATH,
        "wb"
    ) as file:

        pickle.dump(
            incidents,
            file
        )

    print(
        "Historical incident index created successfully."
    )

    return index, incidents


def load_incident_index():

    if (
        not os.path.exists(
            INCIDENT_INDEX_PATH
        )
        or not os.path.exists(
            INCIDENT_DOCUMENTS_PATH
        )
    ):
        return create_incident_index()

    index = faiss.read_index(
        INCIDENT_INDEX_PATH
    )

    with open(
        INCIDENT_DOCUMENTS_PATH,
        "rb"
    ) as file:

        incidents = pickle.load(file)

    return index, incidents


def search_similar_incidents(
    query,
    top_k=3
):

    index, incidents = load_incident_index()

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    )

    faiss.normalize_L2(
        query_embedding
    )

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, index_id in zip(
        scores[0],
        indices[0]
    ):

        if index_id == -1:
            continue

        incident = incidents[index_id]

        results.append({
            "source": incident["source"],
            "content": incident["content"],
            "score": float(score)
        })

    return results


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\nKnowledge search:")

    results = search_knowledge(
        "Kubernetes failed to pull container image",
        top_k=3
    )

    for result in results:

        print("\n-------------------------")

        print(
            f"Source: {result['source']}"
        )

        print(
            f"Similarity: {result['score']:.4f}"
        )


    print("\nHistorical incident search:")

    incidents = search_similar_incidents(
        "Database connection timeout during deployment",
        top_k=3
    )

    for incident in incidents:

        print("\n-------------------------")

        print(
            f"Incident: {incident['source']}"
        )

        print(
            f"Similarity: {incident['score']:.4f}"
        )