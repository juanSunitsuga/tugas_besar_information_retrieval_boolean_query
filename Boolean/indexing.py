import os
import re
import json
from collections import defaultdict
from nltk.stem import PorterStemmer

# Initialize the Porter Stemmer for stemming words
stemmer = PorterStemmer()

# Define the directory containing the documents
input_dir = '../dataset/document'


# Function to tokenize, remove punctuation, and stem words
def process_text(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return [stemmer.stem(word) for word in words]


# Dictionary to hold the inverted index
inverted_index = defaultdict(list)

# Process each document to populate the inverted index
for filename in os.listdir(input_dir):
    if filename.endswith('.txt'):
        # Extract the document ID from the filename
        doc_id = int(filename.split('_')[0])

        # Read the document content
        file_path = os.path.join(input_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Tokenize, clean, and stem the content
        tokens = process_text(content)

        # Update the inverted index with document ID for each term
        for token in set(tokens):  # Use set to avoid duplicate entries per document
            inverted_index[token].append(doc_id)

# Convert dictionary to list for easier JSON serialization
inverted_index = {term: sorted(docs) for term, docs in inverted_index.items()}

# Save the inverted index to a JSON file
with open('../dataset/inverted_index.json', 'w', encoding='utf-8') as f:
    json.dump(inverted_index, f, indent=4)

print("Inverted index created and saved to 'inverted_index.json'.")
