import difflib
import json
import csv
import string
from nltk.stem import PorterStemmer
import requests

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


# Get synonyms for a word using the Datamuse API
def get_synonyms(word):
    url = f'https://api.datamuse.com/words?rel_syn={word}&max=10'
    response = requests.get(url)
    print(f"API Response: {response.json()}")
    data = response.json()
    synonyms = [item['word'] for item in data]
    return synonyms


# Find closest match using difflib
def find_closest_match(term, candidates):
    matches = difflib.get_close_matches(term, candidates, n=1, cutoff=0.8)  # cutoff controls match similarity
    return matches[0] if matches else None


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
        if term == "OR" or term == "NOT":
            translated_terms.append(term)
        else:
            # Add 'AND' between terms not followed by "OR" or "NOT"
            if i > 0 and terms[i - 1] not in {"OR", "NOT"}:
                translated_terms.append("AND")
            translated_terms.append(term)

    # Join the translated terms into the final Boolean query
    boolean_query = ' '.join(translated_terms)
    return boolean_query


def boolean_search(query):
    global inverted_index
    tokens = query.upper().split()
    translator = str.maketrans('', '', string.punctuation)
    filtered_tokens = [word.translate(translator) for word in tokens]
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(word.lower()) for word in filtered_tokens]

    result = None
    current_operation = 'AND'

    for token in stemmed_tokens:
        if token == 'AND':
            current_operation = 'AND'
        elif token == 'OR':
            current_operation = 'OR'
        elif token == 'NOT':
            current_operation = 'NOT'
        else:
            # First, check if the term is in the inverted index
            if token not in inverted_index:
                # Try to get synonyms for the term
                synonyms = get_synonyms(token)
                if synonyms:
                    print(f"Did you mean one of these instead of '{token}'? {', '.join(synonyms)}")
                    # Optionally, you could let the user choose or automatically try the first synonym
                    token = synonyms[0]  # Choose the first synonym as a fallback
                else:
                    # If no synonyms found, use the closest match from difflib
                    closest_match = find_closest_match(token, inverted_index.keys())
                    if closest_match:
                        print(f"Did you mean '{closest_match}' instead of '{token}'?")
                        token = closest_match  # Use the closest match found by difflib

            if token in inverted_index:
                word_set = set(map(int, inverted_index[token]))
                if result is None:
                    result = word_set
                elif current_operation == 'AND':
                    result &= word_set
                elif current_operation == 'OR':
                    result |= word_set
                elif current_operation == 'NOT':
                    result -= word_set
            elif current_operation == 'AND':
                result = set()  # Clear result if no match found

    return list(result) if result else []
