from elasticsearch import Elasticsearch
import json

#Connect to Elasticsearch
es = Elasticsearch(
    [{'host': 'localhost', 'port': 9200}],
    http_auth=('elastic', 'Hd4hRlSdxroHPN=6_u-d')
)

# Define the index name
index_name = "lcfaq_index"

# Delete the index if it exists
if es.indices.exists(index_name):
    es.indices.delete(index=index_name)

# Create a new index
es.indices.create(index=index_name)

# Load your FAQ data
with open("D://Anaconda3//envs//RetFAQ//output_faqs.json", "r") as file:  # Replace with your file path
    faqs = json.load(file)

# Index each FAQ pair in Elasticsearch
for i, faq in enumerate(faqs):
    es.index(index=index_name, id=i, body=faq)
