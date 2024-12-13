import json
import os
import re
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch

# Load pre-trained BERT model and tokenizer
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


# Sanitize filenames for compatibility
def sanitize_filename(filename):
    return re.sub(r'[^\w\s\.-]', '', filename)


# Load document data
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


# Parse document content for metadata
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
    # Ensure defaults for missing fields
    data.setdefault('Name', 'Unknown')
    data.setdefault('Price', 'Unknown')
    data.setdefault('Release_date', 'Unknown')
    data.setdefault('Review_no', 'Unknown')
    return data


# Generate query embedding
def get_query_embedding(query):
    inputs = tokenizer(query, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    cls_embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
    return cls_embedding


# Embedding search
def embedding_search(query, top_k=5):
    if not inverted_index:
        print("Error: Inverted index is empty or not loaded.")
        return {"error": "Inverted index not loaded."}

    query_embedding = get_query_embedding(query)
    if query_embedding is None or len(query_embedding) == 0:
        print("Error: Failed to generate query embedding.")
        return {"error": "Failed to generate query embedding."}

    results = []
    for doc_id, doc_embedding in inverted_index.items():
        if not isinstance(doc_embedding, list) or len(doc_embedding) != len(query_embedding):
            continue  # Skip invalid embeddings
        similarity = cosine_similarity([query_embedding], [doc_embedding])[0][0]
        results.append((int(doc_id), similarity))

    # Sort results by similarity score in descending order
    results = sorted(results, key=lambda x: -x[1])

    # Prepare results with metadata
    final_results = []
    for doc_id, similarity in results[:top_k]:
        if doc_id in document_data:
            doc_metadata = document_data[doc_id]['data']
            final_results.append({
                'id': doc_id,
                'name': doc_metadata.get('Name', 'Unknown'),
                'price': doc_metadata.get('Price', 'Unknown'),
                'release_date': doc_metadata.get('Release_date', 'Unknown'),
                'review_no': doc_metadata.get('Review_no', 'Unknown'),
                'similarity': similarity,
                'path': f"dataset/document/{document_data[doc_id]['sanitized_name']}"
            })

    return final_results


# Initial data loading
load_inverted_index("dataset/pretrained_steam_review_embeddings.json")
load_document_data("dataset/document")
