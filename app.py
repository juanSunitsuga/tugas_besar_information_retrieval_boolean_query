from flask import Flask, render_template, request
from Boolean import booleanQuerySteam

app = Flask(__name__, template_folder='templates')


# Load the inverted index and CSV data (if not already loaded in `booleanQuerySteam.py`)
booleanQuerySteam.load_inverted_index("dataset/inverted_index.json")
csv_data = booleanQuerySteam.load_csv_data("dataset/steam_uncleaned.csv")

@app.route('/')
def index():
    return render_template('index.html')  # This should be your search form page

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    if not query:
        return render_template('index.html', error="Please enter a query.")

    boolean_query = booleanQuerySteam.translate_to_boolean_query(query)  # Translate query to Boolean form
    results = booleanQuerySteam.boolean_search(boolean_query)  # Perform the search

    # Prepare results using the loaded CSV data
    search_results = []
    for doc_id in results:
        if doc_id in csv_data:
            doc = csv_data[doc_id]
            search_results.append({
                'doc_id': doc_id,
                'name': doc.get('Name', 'N/A'),
                'price': doc.get('Price', 'N/A'),
                'release_date': doc.get('Release_date', 'N/A')
            })

    # Render results on a new HTML page
    return render_template('index.html', query=query, results=search_results)


if __name__ == '__main__':
    app.run()
