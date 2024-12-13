import os
import json
import re
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import BertTokenizer, BertForSequenceClassification

# Load pre-trained BERT tokenizer
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)


# Function to extract Review_no from document content
def extract_review_no(content):
    match = re.search(r'Review_no: (\d+)', content)
    return int(match.group(1)) if match else 1  # Default to 1 if not found


# Custom Dataset for Steam reviews
class SteamReviewDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        tokens = self.tokenizer(text, max_length=self.max_len, truncation=True, padding='max_length',
                                return_tensors="pt")
        return {
            'input_ids': tokens['input_ids'].squeeze(0),
            'attention_mask': tokens['attention_mask'].squeeze(0),
            'label': torch.tensor(label, dtype=torch.long)
        }


# Fine-tune BERT model
class BERTFineTuner:
    def __init__(self, model_name, num_labels):
        self.tokenizer = None
        self.model = BertForSequenceClassification.from_pretrained(
            model_name,
            num_labels=num_labels,
            ignore_mismatched_sizes=True
        )
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=5e-5)
        self.criterion = torch.nn.CrossEntropyLoss()

    def train(self, dataloader, epochs):
        self.model.train()
        for epoch in range(epochs):
            total_loss = 0
            for batch in dataloader:
                self.optimizer.zero_grad()
                outputs = self.model(
                    input_ids=batch['input_ids'],
                    attention_mask=batch['attention_mask'],
                    labels=batch['label']
                )
                loss = outputs.loss
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss / len(dataloader)}")

    def save_model(self, output_dir):
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)  # Ensure this is present


# Load and preprocess the dataset
input_dir = '../dataset/document'
texts = []
labels = []
max_len = 512

for filename in os.listdir(input_dir):
    if filename.endswith('.txt'):
        file_path = os.path.join(input_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            review_no = extract_review_no(content)
            texts.append(content)
            labels.append(1 if review_no % 2 == 0 else 0)  # Example label logic: even Review_no as 1, odd as 0

dataset = SteamReviewDataset(texts, labels, tokenizer, max_len)
dataloader = DataLoader(dataset, batch_size=8, shuffle=True)

# Fine-tune the model
num_labels = 2  # Number of classes (e.g., positive and negative)
fine_tuner = BERTFineTuner(model_name, num_labels)
fine_tuner.train(dataloader, epochs=3)

# Save the fine-tuned model
output_dir = "../dataset/fine_tuned_bert"
fine_tuner.save_model(output_dir)
print(f"Fine-tuned model saved to {output_dir}")


# Use the fine-tuned model for embedding extraction
def compute_fine_tuned_embedding(text, model, tokenizer):
    tokens = tokenizer(text, return_tensors='pt', max_length=512, truncation=True, padding='max_length')
    with torch.no_grad():
        outputs = model.bert(**tokens)  # Access the BERT encoder within the fine-tuned model
    return outputs.last_hidden_state[:, 0, :].squeeze().numpy()


# Process documents using the fine-tuned model
doc_embeddings = {}
for filename in os.listdir(input_dir):
    if filename.endswith('.txt'):
        doc_id = int(filename.split('_')[0])
        file_path = os.path.join(input_dir, filename)

        print(f"Processing document: {filename} (ID: {doc_id})")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        embedding = compute_fine_tuned_embedding(content, fine_tuner.model, tokenizer)
        doc_embeddings[doc_id] = embedding.tolist()

# Save embeddings
output_path = '../dataset/fine_tuned_bert_embeddings.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(doc_embeddings, f, indent=4)

print(f"Fine-tuned BERT embeddings saved to {output_path}")
