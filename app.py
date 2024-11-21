import os
import json
import re

from flask import Flask, render_template, request, jsonify
from Boolean import booleanQuerySteam

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    results = booleanQuerySteam.boolean_search(query)  # Get results from boolean_search function

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
