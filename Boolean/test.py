import pandas as pd
import chardet
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Detect file encoding
with open('Global YouTube Statistics.csv', 'rb') as f:
    result = chardet.detect(f.read())
    print(f"Detected Encoding: {result}")

# Load the CSV dataset into a pandas DataFrame with the correct encoding
df = pd.read_csv('Global YouTube Statistics.csv', encoding=result['encoding'])


# Tokenize text
def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()

    # Tokenize the text into individual words
    tokens = word_tokenize(text)

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]

    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    filtered_tokens = [word.translate(translator) for word in filtered_tokens]

    # Remove empty strings from the list
    filtered_tokens = [word for word in filtered_tokens if word]

    # Apply stemming
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(word) for word in filtered_tokens]

    return stemmed_tokens


# Initialize the inverted index and stem mapping
inverted_index = {}

# Iterate over the DataFrame rows
for idx, row in df.iterrows():
    # Preprocess the text in the 'Title' column
    words = []

    # Preprocess 'Title' column
    if 'Title' in df.columns and pd.notnull(row['Title']):
        stemmed_words = preprocess_text(row['Title'])
        words += stemmed_words

    # Preprocess 'Country' column
    if 'Country' in df.columns and pd.notnull(row['Country']):
        stemmed_words = preprocess_text(row['Country'])
        words += stemmed_words

    # Preprocess 'channel_type' column
    if 'channel_type' in df.columns and pd.notnull(row['channel_type']):
        stemmed_words = preprocess_text(row['channel_type'])
        words += stemmed_words

    # Preprocess 'category' column
    if 'category' in df.columns and pd.notnull(row['category']):
        stemmed_words = preprocess_text(row['category'])
        words += stemmed_words

    # Preprocess 'created_month' column
    if 'created_month' in df.columns and pd.notnull(row['created_month']):
        stemmed_words = preprocess_text(row['created_month'])
        words += stemmed_words

    # Add words to the inverted index
    for word in words:
        if word not in inverted_index:
            inverted_index[word] = set()
        inverted_index[word].add(idx)


def translate_to_boolean_query(query):
    # Convert the query to lowercase to handle case-insensitivity
    query = query.lower()

    # Replace 'or' and 'not' with their Boolean equivalents
    query = query.replace(" or ", " OR ").replace(" not ", " NOT ")

    # Split the query into terms
    terms = query.split()

    # Initialize a list to store the final terms
    translated_terms = []

    for i, term in enumerate(terms):
        # If the term is "OR" or "NOT", keep it as is
        if term == "OR" or term == "NOT":
            translated_terms.append(term)
        else:
            # Add 'AND' between terms that are not followed by "OR" or "NOT"
            if i > 0 and terms[i - 1] != "OR" and terms[i - 1] != "NOT":
                translated_terms.append("AND")
            translated_terms.append(term)

    # Join the translated terms into the final Boolean query
    boolean_query = ' '.join(translated_terms)

    return boolean_query


# Boolean query parser (supports AND, OR, NOT)
def boolean_search(query):
    # Split the query into tokens
    tokens = query.upper().split()

    # Remove punctuation from each token
    translator = str.maketrans('', '', string.punctuation)
    filtered_tokens = [word.translate(translator) for word in tokens]

    # Apply stemming to query tokens
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(word.lower()) for word in filtered_tokens]

    # Track the result sets for each operation
    result = set(df.index)  # Start with all documents for AND operations
    current_operation = 'AND'  # Default to AND

    for token in stemmed_tokens:  # Use stemmed_tokens for matching
        if token.upper() == 'AND':
            current_operation = 'AND'
        elif token.upper() == 'OR':
            current_operation = 'OR'
        elif token.upper() == 'NOT':
            current_operation = 'NOT'
        else:
            # Perform the operation based on the current operator
            if token in inverted_index:  # Check for the stemmed token
                word_set = inverted_index[token]
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


def save_results_to_txt(results, filename='search_results.txt'):
    with open(filename, 'w') as file:
        for index, row in results.iterrows():
            file.write(f"Row {index}:\n")
            file.write(f"Title: {row['Title']}\n")
            file.write(f"Youtuber: {row['Youtuber']}\n")
            file.write(f"Category: {row['category']}\n")
            file.write(f"Country: {row['Country']}\n")
            file.write(f"Subscribers: {row['subscribers']}\n")
            file.write(f"Created Month: {row['created_month']}\n")
            file.write(f"Channel Type: {row['channel_type']}\n")
            file.write(f"Video Views: {row['video views']}\n")
            file.write("-" * 40 + "\n")
    print(f"Results saved to {filename}")


# Test the search engine
# Example usage

query = ""
print(f"type !exit to close the program")
while query != "!exit":
    query = input("Query: ")
    if query == "!exit":
        break
    boolean_query = translate_to_boolean_query(query)  # Output: tseries AND music OR movies NOT songs
    results = boolean_search(boolean_query)
    print(f"Search Results for '{query}':\n{results}")

    save_results_to_txt(results)
