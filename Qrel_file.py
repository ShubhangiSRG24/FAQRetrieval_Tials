import pandas as pd
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import docx2txt  # Library for extracting text from Word files

# Connect to Elasticsearch
# es = Elasticsearch(
#     [{'host': 'localhost', 'port': 9200}],
#     http_auth=('elastic', 'Hd4hRlSdxroHPN=6_u-d')
# )

# Load pre-trained SBERT model
model = SentenceTransformer('all-mpnet-base-v2')  #all-mpnet-base-v2   all-MiniLM-L12-v2

# test_embedding = model.encode("This is a test sentence.")
# print(test_embedding)
# Define your Elasticsearch index
#index_name = "user_queries_faqs"
#index_name = "merge_faqs"

# Read user queries from an Excel file
user_queries_df = pd.read_excel("D://Anaconda3//envs//RetFAQ//GenericMergeQ.xlsx")  
user_queries = user_queries_df["text"].tolist()

# Extract FAQ data from the Word file
faq_file_path = 'D://Anaconda3//envs//RetFAQ//FAQbackup_numbered.docx'
faq_text = docx2txt.process(faq_file_path)
#print(faq_text[:500])


# Initialize an empty list to store indexed FAQs
indexed_faqs = []

# Split the FAQ text into individual lines
faq_lines = faq_text.split('\n')

# Initialize variables to keep track of questions and answers
current_question = None
current_answer = []

# Iterate through the lines and construct FAQ pairs
for line in faq_lines:
    line = line.strip()
    if line.startswith("Q") and "." in line:  # Check if line starts with a question
        if current_question is not None:
            # Save the previous question and its answer
            indexed_faqs.append({'question': current_question, 'answer': '\n'.join(current_answer)})
        current_question = line[line.find(".")+1:].strip()  # Extract question text
        current_answer = []
    elif line.startswith("A") and "." in line:  # Check if line starts with an answer
        current_answer.append(line[line.find(".")+1:].strip())  # Append answer text

# Add the last FAQ to the indexed_faqs list
if current_question is not None:
    indexed_faqs.append({'question': current_question, 'answer': '\n'.join(current_answer)})

# print("Number of FAQs:", len(indexed_faqs))
# for faq in indexed_faqs[:5]:  # Print first 5 FAQs for checking
#     print(f"Question: {faq['question']}")

# Initialize FAISS index (assuming you've already created it)
embedding_dim = model.get_sentence_embedding_dimension()
index = faiss.IndexFlatL2(embedding_dim)

# Prepare FAQ embeddings and build FAISS index
faq_embeddings = []

for faq in indexed_faqs:
    question = faq['question']
    question_embedding = model.encode(question)
    # print(question_embedding)
    faq_embeddings.append(np.array(question_embedding, dtype='float32'))

# Convert the list of embeddings to a numpy array
faq_embeddings = np.array(faq_embeddings)

if faq_embeddings.size == 0:
    print("No FAQs to index. The embeddings array is empty.")
else:
    # Ensure the array is 2-dimensional
    if faq_embeddings.ndim == 1:
        faq_embeddings = faq_embeddings.reshape(-1, embedding_dim)
    # print(f"Embeddings shape: {faq_embeddings.shape}")
    # Add embeddings to the index
    index.add(faq_embeddings)

# # Add the embeddings to the FAISS index
# index.add(faq_embeddings)

# QREL file content
qrels = []

# Iterate through user queries
for query_id, user_query in enumerate(user_queries):

    adjusted_query_id = query_id + 1
    print(f"User Query: {user_query}")

    # Vectorize the user's query
    query_embedding = model.encode(user_query).reshape(1, -1)  # Ensure it's a 2D array

    # Perform a semantic similarity search using FAISS
    k = 4  # Retrieve the top 4 results
    D, I = index.search(query_embedding, k)

    # Retrieve the most similar FAQs
    similar_faq_indices = I[0]
    for i, faq_index in enumerate(similar_faq_indices):
        adjusted_faq_index = faq_index + 1
        similar_faq_question = indexed_faqs[faq_index]['question']
        similar_faq_answer = indexed_faqs[faq_index]['answer']
        print(f"FAQ {i + 1}:")
        print(f"Question: {similar_faq_question}")
        print(f"Answer: {similar_faq_answer}\n")

    # Construct QREL lines for the top FAQs
    for i, faq_index in enumerate(similar_faq_indices):
        adjusted_faq_index = faq_index + 1
        relevance = 1 if i < 3 else 0  # Set relevance 1 for the top 3 results, 0 for the rest
        qrels.append(f"{adjusted_query_id} 0 {adjusted_faq_index} {relevance}")

# Debugging: Print the QREL lines
for line in qrels:
    print(line)

# Write the QREL file to a text file
with open("qrels.txt", "w") as qrels_file:
    qrels_file.write("\n".join(qrels))
