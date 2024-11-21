import os
import json
import re

from flask import Flask, render_template, request, jsonify
from Boolean import booleanQuerySteam

app = Flask(__name__, template_folder='templates')

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
def load_document_data(directory_path):
    global document_data
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            if filename.endswith(".txt"):
                # Use regex to extract the number at the start of the filename
                match = re.match(r"(\d+)_", filename)
                if match:
                    doc_id = int(match.group(1))  # Extract the numeric part as the document ID
                    file_path = os.path.join(directory_path, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Parse the content for relevant fields
                        document_data[doc_id] = parse_document_content(content)
        print("Document data loaded successfully.")
        return document_data
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
    return data


# Initial data loading
load_inverted_index("dataset/inverted_index.json")
document = load_document_data("dataset/document")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    results = booleanQuerySteam.boolean_search(query, document)  # Get results from boolean_search function

    # If no results found or error, return a JSON response with error details
    if isinstance(results, dict) and 'error' in results:  # If error is in results (like no results found)
        return jsonify(results)  # Return the error message and suggestions

    # Otherwise, process the results
    print(f"Search Results: {results}")  # Debugging line, remove it in production

    # Pagination setup
    page = int(request.args.get('page', 1))  # Default page is 1
    per_page = 10
    total_results = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = results[start:end]

    # Pass results and pagination data to the template
    return render_template(
        'index.html',
        query=query,
        results=paginated_results,
        total_results=total_results,
        page=page,
        per_page=per_page
    )


if __name__ == '__main__':
    app.run(debug=True)
