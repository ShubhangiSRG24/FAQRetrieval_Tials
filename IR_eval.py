from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

# Connect to Elasticsearch
es = Elasticsearch(
    [{'host': 'localhost', 'port': 9200}],
    http_auth=('elastic', 'Hd4hRlSdxroHPN=6_u-d')
)

# Define a function to retrieve similar FAQs for a user query
def retrieve_similar_faqs(user_query, index_name='faq_index', num_results=50):
    search_body = {
        'query': {
            'match': {
                'question': {
                    'query': user_query,
                    'analyzer': 'standard'
                }
            }
        }
    }

    search_results = es.search(index=index_name, body=search_body, size=num_results)

    similar_faqs = [(hit['_source']['question'], hit['_source']['answer']) for hit in search_results['hits']['hits']]
    return similar_faqs

# User query input
user_query = input("Enter your query: ")

# Retrieve and display the first 50 similar FAQs
similar_faqs = retrieve_similar_faqs(user_query)

for i, (question, answer) in enumerate(similar_faqs, 1):
    print(f"FAQ {i}:")
    print(f"Question: {question}")
    print(f"Answer: {answer}\n")
