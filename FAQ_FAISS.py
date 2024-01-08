import faiss
from elasticsearch import Elasticsearch
import docx2txt
from sentence_transformers import SentenceTransformer, util
import numpy as np 

# Connect to Elasticsearch
es = Elasticsearch(
    [{'host': 'localhost', 'port': 9200}],
    http_auth=('elastic', 'Hd4hRlSdxroHPN=6_u-d')
)

# Load pre-trained SBERT model
model = SentenceTransformer('all-mpnet-base-v2')

# Specify the index settings and mappings
index_name = 'faq_index'
index_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    }
}

# Create the index with the specified settings
es.indices.create(index=index_name, body=index_settings, ignore=400)

def extract_text_from_docx(file_path):
    text = docx2txt.process(file_path)
    return text

def index_faqs_from_file(es, index_name, file_path):
    faq_text = extract_text_from_docx(file_path)
    faqs = [faq.strip() for faq in faq_text.split('\n\n')]

    # Initialize a list to store FAQs as separate documents
    faq_documents = []

    # Separate questions (Q) and answers (A)
    current_question = None
    for line in faqs:
        if line.startswith("Q. "):
            # Start a new question
            current_question = line.replace("Q. ", "")
        elif line.startswith("A. "):
            # Store the question-answer pair as a document
            current_answer = line.replace("A. ", "")
            faq_documents.append({'question': current_question, 'answer': current_answer})

    # Index the FAQ documents
    for i, faq in enumerate(faq_documents):
        es.index(index=index_name, id=i+1, body=faq)

    return faq_documents

# Initialize FAISS index
embedding_dim = model.get_sentence_embedding_dimension()
num_clusters = 32  # Adjust as needed
index = faiss.IndexFlatL2(embedding_dim)

# Specify the path to your Word file
faq_file_path = 'C://Users//SHUBHANGI//Downloads//FAQs_Subject_aspects.docx'

# Index the FAQs and get the documents
indexed_faqs = index_faqs_from_file(es, index_name, faq_file_path)

# Create a list to store embeddings
faq_embeddings = []

# Prepare FAQ embeddings and build FAISS index
for faq in indexed_faqs:
    question = faq['question']
    answer = faq['answer']

    # Vectorize the FAQ using your SentenceTransformer model
    question_embedding = model.encode(question)
    faq_embeddings.append(np.array(question_embedding, dtype='float32'))  # Convert to NumPy array

# Convert the list of embeddings to a numpy array
faq_embeddings = np.array(faq_embeddings)

# Add the embeddings to the FAISS index
index.add(faq_embeddings)

# Query for questions
test_questions = ["Who is laughing cavelier?", "What is the importance of laughing cavelier painting?", "When was laughing cavelier painting made?"]

for question in test_questions:
    print(f"Question: {question}")

    # Vectorize the user's query
    query_embedding = model.encode(question).reshape(1, -1)  # Ensure it's a 2D array

    # Perform a similarity search using FAISS
    k = 1  # Retrieve the top result
    D, I = index.search(query_embedding, k)

    # Retrieve the answer
    similar_faq_index = I[0][0]
    similar_faq_answer = indexed_faqs[similar_faq_index]['answer']
    print("Answer:", similar_faq_answer)

    print("\n")
