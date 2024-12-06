import os
import json
import re

import torch
from transformers import BertTokenizer, BertModel

# Load pre-trained BERT model and tokenizer
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)
model.eval()
print("eval done")

# Define the directory containing the documents
input_dir = '../dataset/document'

# Dictionary to store document embeddings and other metadata
doc_embeddings = {}
review_numbers = {}  # Store Review_no for each document
document_count = 0


# Function to extract Review_no from document content
def extract_review_no(content):
    match = re.search(r'Review_no: (\d+)', content)
    return int(match.group(1)) if match else 1  # Default to 1 if not found


# Function to compute BERT embeddings for a text
def compute_bert_embedding(text):
    tokens = tokenizer(text, return_tensors='pt', max_length=512, truncation=True, padding='max_length')
    with torch.no_grad():
        outputs = model(**tokens)
    # Use the [CLS] token's representation as the document embedding
    return outputs.last_hidden_state[:, 0, :].squeeze().numpy()


# Process each document to extract embeddings
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

        # Compute BERT embedding for the document
        doc_embedding = compute_bert_embedding(content)
        doc_embeddings[doc_id] = {
            "review_no": review_no,
            "embedding": doc_embedding.tolist()  # Convert to list for JSON serialization
        }
        print(f"Document {doc_id} processed")
        document_count += 1

# Save the BERT-based index to a JSON file
output_path = '../dataset/bert_inverted_index.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(doc_embeddings, f, indent=4)

print(f"BERT-based inverted index saved to {output_path}")
