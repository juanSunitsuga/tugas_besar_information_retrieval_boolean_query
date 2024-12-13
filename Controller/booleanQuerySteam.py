import json
import os
import string
import re
from nltk.stem import PorterStemmer

# Global variables to hold loaded data
inverted_index = {}
document_data = {}


# Load the inverted index
def load_inverted_index(file_path):
    global inverted_index
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                inverted_index = json.load(f)
                print("Inverted index loaded successfully.")
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in inverted index file.")
    else:
        print(f"Error: File {file_path} not found.")


def sanitize_filename(filename):
    # Remove or replace invalid characters for filesystem
    return re.sub(r'[^\w\s\.-]', '', filename)  # Removes invalid characters


# Load document data from the `dataset/document` directory
def load_document_data(directory_path):
    global document_data
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            if filename.endswith(".txt"):
                match = re.match(r"(\d+)_", filename)
                if match:
                    doc_id = int(match.group(1))
                    sanitized_name = sanitize_filename(filename)
                    file_path = os.path.join(directory_path, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        document_data[doc_id] = {
                            'original_name': filename,
                            'sanitized_name': sanitized_name,
                            'data': parse_document_content(content)
                        }
        print("Document data loaded successfully.")
    else:
        print(f"Error: Directory {directory_path} not found.")


# Parse the content of a document for specific fields
def parse_document_content(content):
    data = {}
    for line in content.splitlines():
        line = line.strip()
        if "Name:" in line:
            data['Name'] = line.split("Name:", 1)[1].strip()
        elif "Price:" in line:
            data['Price'] = line.split("Price:", 1)[1].strip()
        elif "Release_date:" in line:
            data['Release_date'] = line.split("Release_date:", 1)[1].strip()
        elif "Review_no:" in line:
            data['Review_no'] = line.split("Review_no:", 1)[1].strip()
    # Ensure all fields have default values if missing
    data.setdefault('Name', 'Unknown')
    data.setdefault('Price', 'Unknown')
    data.setdefault('Release_date', 'Unknown')
    data.setdefault('Review_no', 'Unknown')
    return data



# Controller search with ranking
def boolean_search(query):
    tokens = query.upper().split()
    translator = str.maketrans('', '', string.punctuation)
    filtered_tokens = [word.translate(translator) for word in tokens]
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(word.lower()) for word in filtered_tokens]
    result = None
    current_operation = 'and'

    for token in stemmed_tokens:
        if token in {'and', 'or', 'not'}:
            current_operation = token  # Update the current operation
        else:
            if token in inverted_index:
                word_postings = inverted_index[token]["postings"]
                word_set = set(map(int, word_postings.keys()))
            else:
                word_set = set()

            if result is None:
                result = word_set
            elif current_operation == 'and':
                result &= word_set
            elif current_operation == 'or':
                result |= word_set
            elif current_operation == 'not':
                result -= word_set

    if not result:
        print("No results found for the query.")
        return []

    ranked_results = []
    for doc_id in result:
        doc_id_str = str(doc_id)
        score = 0
        for token in stemmed_tokens:
            if token in inverted_index:
                postings = inverted_index[token]["postings"]
                score += postings.get(doc_id_str, 0)
        ranked_results.append((doc_id, score))

    ranked_results.sort(key=lambda x: -x[1])

    # Add metadata and document path
    return [
        {
            'id': doc_id,
            'score': score,
            'name': document_data[doc_id]['data'].get('Name', 'Unknown'),
            'price': document_data[doc_id]['data'].get('Price', 'Unknown'),
            'release_date': document_data[doc_id]['data'].get('Release_date', 'Unknown'),
            'review_no': document_data[doc_id]['data'].get('Review_no', 'Unknown'),
            'path': f"dataset/document/{document_data[doc_id]['sanitized_name']}"
        }
        for doc_id, score in ranked_results
    ]


# Initial data loading
load_inverted_index("dataset/inverted_index_ai.json")
load_document_data("dataset/document")
