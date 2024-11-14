from flask import Flask, render_template, request
from Boolean import booleanQuerySteam

app = Flask(__name__, template_folder='templates')

# Load the inverted index and CSV data
booleanQuerySteam.load_inverted_index("dataset/inverted_index.json")
csv_data = booleanQuerySteam.load_csv_data("dataset/steam_uncleaned.csv")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form.get('query') if request.method == 'POST' else request.args.get('query')
    if not query:
        return render_template('index.html', error="Please enter a query.")

    # Translate and search using Boolean query logic
    boolean_query = booleanQuerySteam.translate_to_boolean_query(query)
    results = booleanQuerySteam.boolean_search(boolean_query)

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

    # Pagination setup
    page = int(request.args.get('page', 1))  # Default page is 1
    per_page = 10
    total_results = len(search_results)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = search_results[start:end]

    return render_template('index.html', query=query, results=paginated_results, total_results=total_results,
                           page=page, per_page=per_page)


if __name__ == '__main__':
    app.run()
