from sentence_transformers import SentenceTransformer, util

# Load the Sentence Transformer model
model = SentenceTransformer('all-mpnet-base-v2')

# Define your documents and query
docs = ["My first paragraph. That contains information", "Python is a programming language"]
query = "What is Python?"

# Encode the documents and query
document_embeddings = model.encode(docs)
query_embedding = model.encode(query)

# Calculate the cosine similarity for each document
cosine_scores = util.pytorch_cos_sim(query_embedding, document_embeddings)

# Find the most similar document and its score
most_similar_index = cosine_scores.argmax()
most_similar_document = docs[most_similar_index]
most_similar_score = cosine_scores[0][most_similar_index].item()

# Print the most similar document and its similarity score
print("Most similar document:", most_similar_document)
print("Cosine similarity score:", most_similar_score)
