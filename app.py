from flask import Flask, render_template, request, jsonify
from Boolean import booleanQuerySteam

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Process the search query from the form submission
        query = request.form['query']
        results = booleanQuerySteam.boolean_search(query)

        if isinstance(results, dict) and 'error' in results:
            return jsonify(results)

        # Set up pagination
        page = 1  # First page for new search
    else:  # Handle GET requests for pagination
        query = request.args.get('query', '')  # Retrieve the query from the URL parameters
        results = booleanQuerySteam.boolean_search(query)

        if isinstance(results, dict) and 'error' in results:
            return jsonify(results)

        page = int(request.args.get('page', 1))  # Retrieve the current page from the URL parameters

    # Pagination logic
    per_page = 10
    total_results = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = results[start:end]

    return render_template(
        'index.html',
        query=query,
        results=paginated_results,
        total_results=total_results,
        page=page,
        per_page=per_page
    )


if __name__ == '__main__':
    app.run()
