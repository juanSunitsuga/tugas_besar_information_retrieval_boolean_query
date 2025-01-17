import json  # For modifying the inverted index.
import os  # Handle file reading, writing, and path operations.
import re  # Perform regular expression-based string manipulation.
import numpy as np  # Work with numerical data.
from sklearn.cluster import KMeans  # Apply K-Means clustering.
from sklearn.preprocessing import StandardScaler  # Normalize features before clustering.


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
    return re.sub(r'[^\w\s\.-]', '', filename)  # Removes invalid characters


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

    data.setdefault('Name', 'Unknown')
    data.setdefault('Price', 'Unknown')
    data.setdefault('Release_date', 'Unknown')
    data.setdefault('Review_no', 'Unknown')
    data.setdefault('Tags', [])

    return data


# Initialize global variables
inverted_index = {}
document_data = {}
load_inverted_index("../dataset/inverted_index_ai.json")
load_document_data("../dataset/document")


def extract_numeric_value(input_string):
    match = re.search(r'\d+', input_string)
    return float(match.group()) if match else 0.0


def prepare_features():
    features = []
    game_ids = []

    for doc_id, data in document_data.items():
        tags = data['data']['Tags']
        price = extract_numeric_value(data['data']['Price']) if data['data']['Price'] != 'Unknown' else 0

        tag_vector = [1 if tag in tags else 0 for tag in inverted_index.keys()]
        features.append(tag_vector + [price])
        game_ids.append(doc_id)

    return np.array(features), game_ids


def perform_clustering(features, game_ids, n_clusters):
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(features_scaled)

    for idx, doc_id in enumerate(game_ids):
        document_data[doc_id]['cluster'] = clusters[idx]

    return clusters


def update_inverted_index_with_clusters(inverted_index, document_data):
    for term, term_data in inverted_index.items():
        if "postings" in term_data:
            for doc_id in list(term_data["postings"].keys()):
                doc_id = int(doc_id)  # Ensure doc_id is an integer
                cluster_id = int(document_data[doc_id].get('cluster'))  # Convert to Python int
                term_data["postings"][str(doc_id)] = {
                    "score": term_data["postings"][str(doc_id)],
                    "cluster": cluster_id
                }
    return inverted_index


def save_updated_inverted_index(file_path, inverted_index):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(inverted_index, f, indent=4)
    print(f"Inverted index updated and saved to {file_path}.")


def main():
    # Load and prepare data
    features, game_ids = prepare_features()

    # Perform clustering
    print("Clustering the games...")
    optimal_k = 30
    clusters = perform_clustering(features, game_ids, n_clusters=optimal_k)

    # Update the inverted index
    print("Updating inverted index with cluster data...")
    updated_inverted_index = update_inverted_index_with_clusters(inverted_index, document_data)

    # Save the updated inverted index
    save_updated_inverted_index("../dataset/inverted_index_ai(30).json", updated_inverted_index)

    # Print clustering results for verification
    for cluster in range(optimal_k):
        print(f"\nCluster {cluster + 1}:")
        cluster_games = [document_data[doc_id]['data']['Name'] for doc_id, c in zip(game_ids, clusters) if c == cluster]
        print(", ".join(cluster_games))


if __name__ == "__main__":
    main()
