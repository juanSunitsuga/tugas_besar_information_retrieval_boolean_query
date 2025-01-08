import os  # For interacting with the filesystem.
import re  # For pattern matching and extracting text using regular expressions.
import json  # For saving the inverted index as a JSON file.
import math  # For mathematical calculations like logarithm.
import string  # For removing punctuation from text.
from collections import defaultdict  # For creating dictionaries with default values.
from nltk.corpus import stopwords  # For filtering out common stop words.
from nltk.stem import PorterStemmer  # For stemming words to their root forms.

# Initialize the Porter Stemmer for stemming words
stemmer = PorterStemmer()

# Define the directory containing the documents
input_dir = '../dataset/document'


# input_dir = 'dataset/document' #Khusus Untuk William FI


# Function to tokenize, remove punctuation, and stem words
def process_text(text):
    # Tokenize the text into words
    tokens = re.findall(r'\b\w+\b', text.lower())

    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    tokens = [word.translate(translator) for word in tokens]

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]

    # Stem the filtered words
    return [stemmer.stem(word) for word in filtered_tokens]


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

        # Tokenize, stop word, and stem the content
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
# output_path = 'dataset/inverted_index.json' #Khusus Untuk William FI
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(inverted_index, f, indent=4)

print("inverted index created successfully!")
