from rank_bm25 import BM25Okapi

corpus = [
    "Hello there good man!",
    "It is quite windy in London",
    "How is the weather today?"
]

tokenized_corpus = [doc.split(" ") for doc in corpus]

bm25 = BM25Okapi(tokenized_corpus)

query = "good"
tokenized_query = query.split(" ")

# Get top matching documents
top_docs = bm25.get_top_n(tokenized_query, corpus, n=1)

# The top_docs variable now contains a list of matching documents
top_matching_doc = top_docs[0]

print(f"The top matching document is: {top_matching_doc}")
