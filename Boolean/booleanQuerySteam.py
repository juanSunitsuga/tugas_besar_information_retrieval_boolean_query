import json
import csv
import string
from nltk.stem import PorterStemmer

# Global variable for inverted index
inverted_index = {}

# Load the inverted index from a JSON file
def load_inverted_index(file_path):
    global inverted_index
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            inverted_index = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at path {file_path}")
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON from file {file_path}")

# Load the CSV file and create a mapping of row index (document ID) to the information
def load_csv_data(file_path):
    data = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for index, row in enumerate(reader, start=1):  # Start indexing from 1
                data[index] = row  # Use row index as the document ID
    except FileNotFoundError:
        print(f"Error: File not found at path {file_path}")
    return data

# Translate a query to a Boolean form
def translate_to_boolean_query(query):
    query = query.lower()  # Convert the query to lowercase for case-insensitivity
    query = query.replace(" or ", " OR ").replace(" not ", " NOT ")  # Replace 'or' and 'not'
    terms = query.split()  # Split the query into terms
    translated_terms = []

    for i, term in enumerate(terms):
        if term == "OR" or term == "NOT":  # Keep "OR" or "NOT" as is
            translated_terms.append(term)
        else:
            # Add 'AND' between terms not followed by "OR" or "NOT"
            if i > 0 and terms[i - 1] not in {"OR", "NOT"}:
                translated_terms.append("AND")
            translated_terms.append(term)

    # Join the translated terms into the final Boolean query
    boolean_query = ' '.join(translated_terms)
    return boolean_query

# Boolean query parser (supports AND, OR, NOT)
def boolean_search(query):
    global inverted_index  # Use the global inverted_index variable
    tokens = query.upper().split()  # Split the query into tokens
    translator = str.maketrans('', '', string.punctuation)
    filtered_tokens = [word.translate(translator) for word in tokens]
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(word.lower()) for word in filtered_tokens]  # Apply stemming

    result = None
    current_operation = 'AND'

    for token in stemmed_tokens:
        if token.upper() == 'AND':
            current_operation = 'AND'
        elif token.upper() == 'OR':
            current_operation = 'OR'
        elif token.upper() == 'NOT':
            current_operation = 'NOT'
        else:
            if token in inverted_index:  # Check for the stemmed token in the inverted index
                word_set = set(map(int, inverted_index[token]))  # Convert doc IDs to int if needed
                if result is None:  # Initialize result if this is the first term
                    result = word_set
                elif current_operation == 'AND':
                    result &= word_set
                elif current_operation == 'OR':
                    result |= word_set
                elif current_operation == 'NOT':
                    result -= word_set
            elif current_operation == 'AND':
                result = set()

    return list(result) if result else []

# Save the search results to a text file
def save_results_to_txt(results, data, filename='search_results_steam.txt'):
    with open(filename, 'w', encoding='utf-8') as file:
        if not results:
            file.write("No matching documents found.\n")
        else:
            for doc_id in results:
                if doc_id in data:
                    doc = data[doc_id]
                    file.write(f"Row {doc_id}:\n")
                    file.write(f"Name: {doc.get('Name', 'N/A')}\n")
                    file.write(f"Price: {doc.get('Price', 'N/A')}\n")
                    file.write(f"Release_date: {doc.get('Release_date', 'N/A')}\n")
                    file.write("-" * 40 + "\n")
    print(f"Results saved to {filename}")

# Load data
load_inverted_index('../dataset/inverted_index.json')
csv_data = load_csv_data('../dataset/steam_uncleaned.csv')

# Start the query loop
query = ""
print("Type !exit to close the program")
while query != "!exit":
    query = input("Query: ")
    if query == "!exit":
        break

    # Translate the query to Boolean form and perform the search
    boolean_query = translate_to_boolean_query(query)
    results = boolean_search(boolean_query)

    # Display and save results
    print(f"Matching document IDs for '{query}': {results}")
    save_results_to_txt(results, csv_data)
