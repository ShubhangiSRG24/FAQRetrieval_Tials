from elasticsearch import Elasticsearch
import docx2txt
from sentence_transformers import SentenceTransformer, util


# Connect to Elasticsearch
es = Elasticsearch(
    [{'host': 'localhost', 'port': 9200}],
    http_auth=('elastic', 'Hd4hRlSdxroHPN=6_u-d')
)

# Load pre-trained SBERT model
#model = SentenceTransformer('paraphrase-mpnet-base-v2')
model = SentenceTransformer('all-mpnet-base-v2')
# multi-qa-mpnet-base-dot-v1, all-mpnet-base-v2

# Specify the index settings and mappings
index_name = 'faq_index'
index_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0  # Set the number of replicas as needed
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

# Define the Elasticsearch index name
index_name = 'faq_index'

# Specify the path to your Word file
faq_file_path = 'C://Users//SHUBHANGI//Downloads//FAQs_Subject_aspects.docx'

# Index the FAQs and get the documents
indexed_faqs = index_faqs_from_file(es, index_name, faq_file_path)

# # Print the indexed documents
# for i, faq in enumerate(indexed_faqs, start=1):
#     print(f"Document {i}:\nQuestion: {faq['question']}\nAnswer: {faq['answer']}\n")

# Query for questions
test_questions = ["Who is laughing cavelier?", "What is the importance of laughing cavelier painting?", "When was laughing cavelier painting made?"]

for question in test_questions:
    print(f"Question: {question}")

    # Perform keyword-based search in Elasticsearch
    response = es.search(index=index_name, body={
        'query': {
            'match': {
                'question': question
            }
        }
    })

    # Extract the top retrieved questions
    top_retrieved = [hit['_source']['answer'] for hit in response['hits']['hits']]

    # Compute BERT-style scoring for question answering
    question_embeddings = model.encode(question, convert_to_tensor=True)
    faq_embeddings = model.encode(top_retrieved, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(question_embeddings, faq_embeddings)

    # Find the answer with the highest similarity
    best_answer_index = similarities.argmax().item()
    answer = top_retrieved[best_answer_index]
    
    print("Answer:", answer)
    print("\n")