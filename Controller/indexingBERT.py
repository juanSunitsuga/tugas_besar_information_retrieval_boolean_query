import os
import json
import re
import torch
from transformers import BertTokenizer, BertModel

# Load pre-trained BERT tokenizer and model
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)
pretrained_model = BertModel.from_pretrained(model_name)


# Function to preprocess review text (specific to Steam reviews)
def preprocess_steam_review(content):
    """
    Cleans and preprocesses Steam review text.
    """
    # Example: Remove "Pros:" and "Cons:" sections if present
    content = re.sub(r'Pros:\s*.*', '', content, flags=re.DOTALL)
    content = re.sub(r'Cons:\s*.*', '', content, flags=re.DOTALL)
    content = re.sub(r'[^\w\s]', '', content)  # Remove non-alphanumeric characters
    return content.strip()


# Function to compute embeddings using the pre-trained model
def compute_pretrained_embedding(text, model, tokenizer):
    tokens = tokenizer(text, return_tensors='pt', max_length=512, truncation=True, padding='max_length')
    with torch.no_grad():
        outputs = model(**tokens)
    # Use the [CLS] token embedding as the sentence-level embedding
    return outputs.last_hidden_state[:, 0, :].squeeze().numpy()


# Load and preprocess Steam reviews
input_dir = '../dataset/document'  # Adjust path for your Steam reviews dataset
doc_embeddings = {}

for filename in os.listdir(input_dir):
    if filename.endswith('.txt'):  # Ensure input is in text format
        review_id = int(filename.split('_')[0])  # Example: Extract ID from filename like '123_review.txt'
        file_path = os.path.join(input_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Preprocess the Steam review content
        processed_text = preprocess_steam_review(content)

        # Compute embeddings
        embedding = compute_pretrained_embedding(processed_text, pretrained_model, tokenizer)
        doc_embeddings[review_id] = embedding.tolist()

# Save embeddings
output_path = '../dataset/pretrained_steam_review_embeddings.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(doc_embeddings, f, indent=4)

print(f"Pre-trained BERT embeddings for Steam reviews saved to {output_path}")
