import os
import re
import json
import math
from collections import defaultdict
from nltk.stem import PorterStemmer
from gensim.models import Word2Vec

# Initialize the Porter Stemmer for stemming words
stemmer = PorterStemmer()

# Define the directory containing the documents
input_dir = '../dataset/document'


# Function to tokenize, remove punctuation, and stem words
def process_text(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return [stemmer.stem(word) for word in words]


# Function to tokenize and clean text for Word2Vec training
def tokenize_text(text):
    return re.findall(r'\b\w+\b', text.lower())


# Read all documents and prepare a tokenized corpus for Word2Vec
corpus = []
for filename in os.listdir(input_dir):
    if filename.endswith('.txt'):
        file_path = os.path.join(input_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            tokens = tokenize_text(content)
            corpus.append(tokens)

# Train a Word2Vec model on the corpus
print("Training Word2Vec model...")
model = Word2Vec(sentences=corpus, vector_size=100, window=5, min_count=1, workers=4)
word_vectors = model.wv  # Extract word vectors
print("Word2Vec model trained successfully!")


# Helper function to extract Review_no from document content
def extract_review_no(content):
    match = re.search(r'Review_no: (\d+)', content)
    return int(match.group(1)) if match else 1  # Default to 1 if not found


# Dictionary to hold term frequencies, document lengths, and review numbers
doc_term_freq = defaultdict(lambda: defaultdict(int))
doc_lengths = defaultdict(int)
review_numbers = {}  # Store Review_no for each document
document_count = 0

# Process each document to populate term frequencies
for filename in os.listdir(input_dir):
    if filename.endswith('.txt'):
        # Extract the document ID from the filename
        doc_id = int(filename.split('_')[0])

        # Read the document content
        file_path = os.path.join(input_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract Review_no for document rank
        review_no = extract_review_no(content)
        review_numbers[doc_id] = review_no

        # Tokenize, clean, and stem the content
        tokens = process_text(content)
        document_count += 1

        # Calculate term frequencies and document length
        for token in tokens:
            doc_term_freq[doc_id][token] += 1
            doc_lengths[doc_id] += 1

# Calculate IDF for each term
term_document_count = defaultdict(int)
for doc_id, terms in doc_term_freq.items():
    for term in terms.keys():
        term_document_count[term] += 1

idf = {term: math.log(document_count / (1 + term_document_count[term])) for term in term_document_count}

# Build the inverted index with the desired structure
inverted_index = {}
for term, idf_value in idf.items():
    postings = {}
    semantic_terms = {}

    # Find semantically similar terms using Word2Vec
    if term in word_vectors:
        similar_words = word_vectors.most_similar(term, topn=5)  # Top 5 similar terms
        semantic_terms = {word: similarity for word, similarity in similar_words}

    for doc_id, terms in doc_term_freq.items():
        if term in terms:
            tf = doc_term_freq[doc_id][term] / doc_lengths[doc_id]
            tfidf = tf * idf_value
            postings[str(doc_id)] = tfidf

    inverted_index[term] = {
        "idf": idf_value,
        "postings": postings,
        "semantic_terms": semantic_terms,  # Add semantic terms to index
    }

# Save the inverted index to a JSON file
output_path = '../dataset/inverted_index.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(inverted_index, f, indent=4)

print("AI-enhanced inverted index created successfully!")
