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
    # stemmer = PorterStemmer()
    # stemmed_tokens = [stemmer.stem(word) for word in filtered_tokens]

    return filtered_tokens


# Initialize the inverted index as a Dictionary
inverted_index = {}

# Iterate over the DataFrame rows
for idx, row in df.iterrows():
    # Preprocess the text in the 'Title' column
    words = []

    # Preprocess 'Title' column
    if 'Title' in df.columns and pd.notnull(row['Title']):
        words += preprocess_text(row['Title'])

    # Preprocess 'Country' column
    if 'Country' in df.columns and pd.notnull(row['Country']):
        words += preprocess_text(row['Country'])

    # Preprocess 'channel_type' column
    if 'channel_type' in df.columns and pd.notnull(row['channel_type']):
        words += preprocess_text(row['channel_type'])

    # Add words to the inverted index
    for word in words:
        if word not in inverted_index:
            inverted_index[word] = set()
        inverted_index[word].add(idx)


# Boolean query parser (supports AND, OR, NOT)
def boolean_search(query):
    # Split the query into tokens
    tokens = query.upper().split()

    # Remove punctuation from each token
    translator = str.maketrans('', '', string.punctuation)
    filtered_tokens = [word.translate(translator) for word in tokens]

    # Track the result sets for each operation
    result = set(df.index)  # Start with all documents for AND operations
    current_operation = 'AND'  # Default to AND

    for token in filtered_tokens:
        if token == 'AND':
            current_operation = 'AND'
        elif token == 'OR':
            current_operation = 'OR'
        elif token == 'NOT':
            current_operation = 'NOT'
        else:
            # Perform the operation
            token = token.lower()  # Lowercase the token
            if token in inverted_index:
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
            file.write(f"Country: {row['Country']}\n")
            file.write(f"Subscribers: {row['subscribers']}\n")
            file.write(f"Channel Type: {row['channel_type']}\n")
            file.write(f"Video Views: {row['video views']}\n")
            file.write("-" * 40 + "\n")
    print(f"Results saved to {filename}")


# Test the search engine
query = "T-Series OR Movies OR Beast NOT Nursery"
results = boolean_search(query)
print(f"Search Results for '{query}':\n{results}")

save_results_to_txt(results)
