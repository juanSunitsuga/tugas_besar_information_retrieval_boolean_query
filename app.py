from flask import Flask, render_template, request, jsonify, send_from_directory
from Controller import booleanQuerySteam
from Controller import embeddedQuerySteam
import os

app = Flask(__name__, template_folder='templates')

# Route for the main index page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle search functionality
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

# Function to parse the .txt file
def parse_txt_file(file_path):
    data = {}

    try:
        with open(file_path, 'r') as file:
            # Read the lines of the file
            lines = file.readlines()

            # Extract information from each line
            for line in lines:
                if line.startswith("Name:"):
                    data['name'] = line[len("Name:"):].strip()
                elif line.startswith("Price:"):
                    data['price'] = line[len("Price:"):].strip()
                elif line.startswith("Release_date:"):
                    data['release_date'] = line[len("Release_date:"):].strip()
                elif line.startswith("Review_no:"):
                    data['review_no'] = line[len("Review_no:"):].strip()
                elif line.startswith("Review_type:"):
                    data['review_type'] = line[len("Review_type:"):].strip()
                elif line.startswith("Tags:"):
                    data['tags'] = line[len("Tags:"):].strip()
                elif line.startswith("Description:"):
                    data['description'] = line[len("Description:"):].strip()
    except FileNotFoundError:
        data = None
    except Exception as e:
        print(f"Error reading the file: {e}")
        data = None

    return data

# Route to display game details dynamically
@app.route('/game_details.html/<string:path>')
def game_details(path):
    # Build the correct file path
    real_path = os.path.join("dataset", "document", path)
    
    # Parse the file to get game details
    file_content = parse_txt_file(real_path)

    if not file_content:
        return "Game details not found", 404

    # Pass the parsed data to the game_details template
    return render_template('game_details.html', game=file_content)



# Run the application
if __name__ == '__main__':
    app.run()
