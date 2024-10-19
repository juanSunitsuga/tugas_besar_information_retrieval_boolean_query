import pandas as pd
import re
import chardet

# Detect file encoding
with open('Global YouTube Statistics.csv', 'rb') as f:
    result = chardet.detect(f.read())
    print(result)

# Load the CSV dataset into a pandas DataFrame
df = pd.read_csv('Global YouTube Statistics.csv', encoding='ISO-8859-1')
print(df.columns)


# Preprocessing: Clean and tokenize text (you can extend this function)
def preprocess_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\W+', ' ', text)  # Remove punctuation
    words = text.split()  # Tokenize
    return words


# Build an inverted index
inverted_index = {}
for idx, row in df.iterrows():
    # Assuming the text to search is in a column named 'Title'
    words = preprocess_text(row['Title'])
    for word in words:
        if word not in inverted_index:
            inverted_index[word] = set()
        inverted_index[word].add(idx)


# Boolean query parser (supports AND, OR, NOT)
def boolean_search(query):
    # Split the query into tokens
    tokens = query.upper().split()

    # Track the result sets for each operation
    result = set(df.index)  # Start with all documents for AND operations
    current_operation = 'AND'  # Default to AND

    for token in tokens:
        if token == 'AND':
            current_operation = 'AND'
        elif token == 'OR':
            current_operation = 'OR'
        elif token == 'NOT':
            current_operation = 'NOT'
        else:
            # Perform the operation based on the current operator
            if token.lower() in inverted_index:
                word_set = inverted_index[token.lower()]
                if current_operation == 'AND':
                    result = result.intersection(word_set)
                elif current_operation == 'OR':
                    result = result.union(word_set)
                elif current_operation == 'NOT':
                    result = result.difference(word_set)
            else:
                # If the word is not in the index, treat it as an empty set
                if current_operation == 'AND':
                    result = set()  # No matches if the word isn't found
                elif current_operation == 'NOT':
                    pass  # Keep the result unchanged if NOT word isn't found

    # Return the rows that match the query
    return df.loc[list(result)]


# Test the search engine
query = "word1 AND word2 OR word3 NOT word4"
results = boolean_search(query)
print(results)
