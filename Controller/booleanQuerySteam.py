import json  # load and save data like the JSON inverted index.
import os  # For interacting with the file system, e.g., reading files and checking file/directory existence.
import string  # For handling strings and removing punctuation.
import re  # For working with regular expressions to parse and process text.
from nltk.stem import PorterStemmer  # For stemming words to their root forms (e.g., "running" -> "run").
from nltk.corpus import stopwords  # For removing common stop words (e.g., "the", "and") during text processing.
import difflib  # For approximate string matching, used for correcting and finding similar terms in a dictionary.


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
        elif "Tags:" in line:
            data['Tags'] = line.split("Tags:", 1)[1].strip().split(",")

    # Ensure all fields have default values if missing
    data.setdefault('Name', 'Unknown')
    data.setdefault('Price', 'Unknown')
    data.setdefault('Release_date', 'Unknown')
    data.setdefault('Review_no', 'Unknown')
    data.setdefault('Tags', 'Unknown')

    return data


def get_closest_matches(word, dictionary, cutoff=0.8):
    matches = difflib.get_close_matches(word, dictionary, n=1, cutoff=cutoff)
    return matches[0] if matches else word


def boolean_search(query):
    tokens = query.upper().split()

    translator = str.maketrans('', '', string.punctuation)
    filtered_tokens = [word.translate(translator) for word in tokens]

    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in filtered_tokens if word.lower() not in stop_words]

    stemmer = PorterStemmer()

    # Separate sentences into words, stem them, and find closest matches
    corrected_tokens = []
    inverted_index_keys = list(inverted_index.keys())

    for token in filtered_tokens:
        # Split token into words if it appears to be a sentence
        words = token.split()
        corrected_words = [
            get_closest_matches(stemmer.stem(word.lower()), inverted_index_keys, cutoff=0.8)
            for word in words
        ]
        corrected_tokens.append(" ".join(corrected_words))  # Rebuild corrected sentence

    result = None
    current_operation = 'and'

    for token in corrected_tokens:
        print(token)
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
        cluster = 0
        for token in corrected_tokens:
            if token in inverted_index:
                postings = inverted_index[token]["postings"]
                posting_data = postings.get(doc_id_str, {})
                score += posting_data.get("score", 0)
                cluster = posting_data.get("cluster", -1)
        ranked_results.append((doc_id, score, cluster))

    ranked_results.sort(key=lambda x: -x[1])

    # Add metadata and document path
    return [
        {
            'id': doc_id,
            'score': score,
            'cluster': cluster,
            'original_name': document_data[doc_id].get('original_name', 'Unknown'),
            'name': document_data[doc_id]['data'].get('Name', 'Unknown'),
            'price': document_data[doc_id]['data'].get('Price', 'Unknown'),
            'release_date': document_data[doc_id]['data'].get('Release_date', 'Unknown'),
            'review_no': document_data[doc_id]['data'].get('Review_no', 'Unknown'),
            'tags': document_data[doc_id]['data'].get('Tags', 'Unknown'),
            'path': f"dataset/document/{document_data[doc_id]['sanitized_name']}",
            'rec_path': f"{document_data[doc_id]['sanitized_name']}"
        }
        for doc_id, score, cluster in ranked_results
    ]


# Initial data loading
load_inverted_index("dataset/inverted_index_ai.json")
load_document_data("dataset/document")
