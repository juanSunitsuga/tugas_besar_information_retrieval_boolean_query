from flask import Flask, render_template, request, jsonify, send_from_directory
from Controller import booleanQuerySteam
from Controller import embeddedQuerySteam

app = Flask(__name__, template_folder='templates')


# Route for the main index page
@app.route('/')
def index():
    return render_template('index.html')


# Route to handle search functionality
@app.route('/search', methods=['GET', 'POST'])
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        method = request.form.get('method', 'boolean')

        if method == 'boolean':
            results = booleanQuerySteam.boolean_search(query)
        elif method == 'embedding':
            results = embeddedQuerySteam.embedding_search(query)
        else:
            return jsonify({"error": f"Unsupported search method '{method}'."})

        if isinstance(results, dict) and 'error' in results:
            return jsonify(results)

        page = 1
    else:
        query = request.args.get('query', '')
        method = request.args.get('method', 'boolean')

        if method == 'boolean':
            results = booleanQuerySteam.boolean_search(query)
        elif method == 'embedding':
            results = embeddedQuerySteam.embedding_search(query)
        else:
            return jsonify({"error": f"Unsupported search method '{method}'."})

        if isinstance(results, dict) and 'error' in results:
            return jsonify(results)

        page = int(request.args.get('page', 1))

    per_page = 10
    total_results = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = results[start:end]

    # Add sanitized names for links
    for result in paginated_results:
        doc_id = result['id']
        document = booleanQuerySteam.document_data.get(doc_id, {})
        result['original_name'] = document.get('original_name', 'Unknown')
        result['sanitized_name'] = document.get('sanitized_name', 'unknown')

    return render_template(
        'index.html',
        query=query,
        results=paginated_results,
        total_results=total_results,
        page=page,
        per_page=per_page,
        method=method
    )


# Serve static files for the dataset/document directory
@app.route('/dataset/document/<path:filename>')
def serve_document(filename):
    return send_from_directory('dataset/document', filename)


# Run the application
if __name__ == '__main__':
    app.run()
