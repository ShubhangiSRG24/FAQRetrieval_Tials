from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch(
    [{'host': 'localhost', 'port': 9200}],
    http_auth=('elastic', 'Hd4hRlSdxroHPN=6_u-d')  # Replace with your credentials
)

# Define the index name
index_name = "lcfaq_index"

# Query to retrieve documents
query = {
    "query": {
        "match_all": {}
    }
}

# Fetch documents from the index
response = es.search(index=index_name, body=query, size=10)  # Adjust the size as needed

# Print the documents along with their index and ID
for doc in response['hits']['hits']:
    print(f"Index: {doc['_index']}, ID: {doc['_id']}, Document: {doc['_source']}")
