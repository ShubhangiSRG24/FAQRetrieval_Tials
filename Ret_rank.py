import faiss
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import numpy as np

# Connect to Elasticsearch
es = Elasticsearch(
    [{'host': 'localhost', 'port': 9200}],
    http_auth=('elastic', 'Hd4hRlSdxroHPN=6_u-d')
)

# Load pre-trained SBERT model
model = SentenceTransformer('all-mpnet-base-v2')

def retrieve_from_elasticsearch(es, user_query, k):
    search_body = {
        "query": {
            "match": {
                "q": user_query  # Replace "q" with the field name where your questions are stored in Elasticsearch
            }
        }
    }

    results = es.search(index='faq_index', body=search_body, size=k)
    candidate_pairs = [(hit['_source']['question'], hit['_source']['answer']) for hit in results['hits']['hits']]
    return candidate_pairs

def rerank_with_faiss(user_query, candidate_pairs, faiss_index, model):
    # Encode the user query
    query_embedding = model.encode(user_query)
    query_embedding = query_embedding[0].astype('float32')

    # Encode the candidate questions
    candidate_question_embeddings = model.encode([q for q, _ in candidate_pairs])
    candidate_question_embeddings = np.array(candidate_question_embeddings).astype('float32')

    # Perform a similarity search using FAISS to get the index (I)
    k = len(candidate_pairs)  # Retrieve all candidate pairs
    I = faiss_index.search(np.array([query_embedding]), k)

    # Re-rank the candidate pairs based on FAISS similarity scores (I)
    re_ranked_pairs = [(candidate_pairs[I[0][i]][0], candidate_pairs[I[0][i]][1]) for i in range(k)]

    return re_ranked_pairs

# Initialize FAISS index
embedding_dim = model.get_sentence_embedding_dimension()
index = faiss.IndexFlatL2(embedding_dim)

# Specify the user's query
user_query = "Your user query here"

# Retrieve top-k candidate pairs from Elasticsearch
topk = 10  # Replace with your desired value
candidate_pairs = retrieve_from_elasticsearch(es, user_query, topk)

# Re-rank the candidate pairs using FAISS
re_ranked_pairs = rerank_with_faiss(user_query, candidate_pairs, index, model)

# Now, re_ranked_pairs contains the top-k candidate pairs re-ranked based on the user query similarity using FAISS
for i, (question, answer, similarity_score) in enumerate(re_ranked_pairs, start=1):
    print(f"Rank {i}:")
    print("Question:", question)
    print("Answer:", answer)
    print("Similarity Score:", similarity_score)
    print()
