import json
import os
import re
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch

# from sentence_transformers import SentenceTransformer
# model = SentenceTransformer('all-MiniLM-L6-v2')


# Load a pre-trained BERT model and tokenizer (one-time initialization)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

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


# Load document data from the `dataset/document` directory

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
        if "Name:" in line:
            data['Name'] = line.split("Name:", 1)[1].strip()
        elif "Price:" in line:
            data['Price'] = line.split("Price:", 1)[1].strip()
        elif "Release_date:" in line:
            data['Release_date'] = line.split("Release_date:", 1)[1].strip()
        elif "Review_no:" in line:
            data['Review_no'] = line.split("Review_no:", 1)[1].strip()

    # Set defaults for missing fields
    data.setdefault('Name', 'Unknown')
    data.setdefault('Price', 'Unknown')
    data.setdefault('Release_date', 'Unknown')
    data.setdefault('Review_no', 'Unknown')

    return data


def get_query_embedding(query):
    """
    Generates a 768-dimensional embedding for the input query using a pre-trained BERT model.
    """
    # Tokenize the input query
    inputs = tokenizer(query, return_tensors="pt", padding=True, truncation=True, max_length=512)

    # Pass the tokens through the model to get embeddings
    with torch.no_grad():
        outputs = model(**inputs)

    # Get the [CLS] token embedding, typically used for sentence embeddings
    cls_embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()

    return cls_embedding


# Embedding search
def embedding_search(query, top_k=5):
    if not inverted_index:
        print("Error: Inverted index is empty or not loaded.")
        return {"error": "Inverted index not loaded."}

    query_embedding = get_query_embedding(query)

    results = []
    for doc_id, doc_embedding in inverted_index.items():
        if not isinstance(doc_embedding, list):  # Ensure it's a valid list
            continue

        similarity = cosine_similarity([query_embedding], [doc_embedding])[0][0]
        results.append((int(doc_id), similarity))

    # Sort results by similarity score in descending order
    results = sorted(results, key=lambda x: -x[1])

    # Prepare the final results with metadata from `document_data`
    final_results = []
    for doc_id, similarity in results[:top_k]:
        document = document_data.get(doc_id, {}).get('data', {})
        final_results.append({
            'id': doc_id,
            'name': document.get('Name', 'Unknown'),
            'price': document.get('Price', 'Unknown'),
            'release_date': document.get('Release_date', 'Unknown'),
            'review_no': document.get('Review_no', 'Unknown'),
            'similarity': similarity
        })

    return final_results



# Initial data loading
load_inverted_index("dataset/pretrained_steam_review_embeddings.json")
load_document_data("dataset/document")
