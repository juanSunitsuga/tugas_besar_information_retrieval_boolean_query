import difflib
import math
import string
from nltk.stem import PorterStemmer
import requests
import re

# Global variable for inverted index
from tugas_besar_information_retrieval_boolean_query.app import inverted_index

# Get synonyms for a word using the Datamuse API
def get_synonyms(word):
    url = f'https://api.datamuse.com/words?rel_syn={word}&max=10'
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an error for HTTP issues
        data = response.json()  # Parse the JSON response
        if data:  # Check if the response contains any data
            synonyms = [item['word'] for item in data]
            print(f"Synonyms for '{word}': {synonyms}")
            return synonyms
        else:
            print(f"No synonyms found for '{word}'.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to fetch synonyms for '{word}'. Exception: {e}")
        return []


# Find closest match using difflib
def find_closest_match(term, candidates):
    matches = difflib.get_close_matches(term, candidates, n=1, cutoff=0.8)  # cutoff controls match similarity
    return matches[0] if matches else None


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


# Boolean search with ranking
def boolean_search(query, document):

    tokens = query.upper().split()
    translator = str.maketrans('', '', string.punctuation)
    filtered_tokens = [word.translate(translator) for word in tokens]
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(word.lower()) for word in filtered_tokens]
    result = None
    current_operation = 'and'

    for token in stemmed_tokens:
        print("token : ", token)
        if token in {'and', 'or', 'not'}:
            current_operation = token  # Update the current operation
        else:
            print("Masuk else")
            if token in inverted_index:
                word_postings = inverted_index[token]["postings"]
                word_set = set(map(int, word_postings.keys()))
                print("Masuk else if")
                if result is None:
                    result = word_set
                elif current_operation == 'and':
                    result &= word_set
                elif current_operation == 'or':
                    result |= word_set
                elif current_operation == 'not':
                    result -= word_set
            else:
                print("Masuk else else")
                # Fallback to synonyms or suggestions
                synonyms = get_synonyms(token)
                if synonyms:
                    token = synonyms[0]
                else:
                    closest_match = find_closest_match(token, inverted_index.keys())
                    if closest_match:
                        token = closest_match
                    else:
                        print(f"No results or suggestions for '{token}'. Skipping.")

    if not result:
        print("No results found for the query. Providing suggestions...")
        return {"error": "No results found", "suggestions": []}

    ranked_results = []
    review_numbers = {
        int(doc_id): extract_review_no(data.get('Review_no', doc_id))
        for doc_id, data in document.items()
    }
    for doc_id in result:
        doc_id_str = str(doc_id)
        for token in stemmed_tokens:
            if token in inverted_index:
                postings = inverted_index[token]["postings"]
                tfidf = postings.get(doc_id_str, 0)
                rank = review_numbers.get(doc_id, 1)
                weighted_score = tfidf * math.log(1 + rank)
                ranked_results.append((doc_id, weighted_score, rank))

    ranked_results.sort(key=lambda x: (-x[2], -x[1]))
    return [(doc_id, score) for doc_id, score, rank in ranked_results]


# Extract numeric review numbers from a review string
def extract_review_no(review_string):
    match = re.search(r'[\d,]+', review_string)
    if match:
        return int(match.group(0).replace(',', ''))
    return 0
