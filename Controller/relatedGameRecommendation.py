from Controller import booleanQuerySteam


# AI Agent
def calculate_similarity(target_tags, target_price, doc_tags, doc_price, weight_tags=0.7, weight_score=0.3):
    """Calculate weighted similarity based on tags and score."""
    # Tag similarity (Jaccard index)
    # Calculate the ratio of the overlapping tags to the overall tags
    tag_similarity = len(set(target_tags) & set(doc_tags)) / len(set(target_tags) | set(doc_tags))

    # Score similarity (inverted normalized difference)
    # Calculate the ratio of the difference price to the highest price
    score_similarity = 1 - abs(target_price - doc_price) / max(1, target_price, doc_price)

    # Weighted similarity
    overall_similarity = weight_tags * tag_similarity + weight_score * score_similarity
    return tag_similarity, score_similarity, overall_similarity


# Start state is when being called e.g.(in app.py)
def recommend_related_games(target_game_tags, target_game_price, top_n=5, doc_id=None):
    """Find and recommend related games."""
    # Perform a boolean search for documents with matching tags
    search_query = " OR ".join(target_game_tags)
    search_results = booleanQuerySteam.boolean_search(search_query)

    if not search_results:
        return []

    recommendations = []

    # Compare target game with search results
    for doc in search_results:
        # x = doc.get('price', 0)
        x = ''.join(c for c in doc.get('price', 0) if c in "1234567890.")
        doc_tags = booleanQuerySteam.inverted_index.get(doc['id'], {}).get("tags", [])
        doc_price = float(0 if len(x) == 0 else x)
        # Calculate similarity
        tag_similarity, score_similarity, overall_similarity = calculate_similarity(
            target_tags=target_game_tags,
            target_price=target_game_price,
            doc_tags=doc_tags,
            doc_price=doc_price
        )
        if doc['id'] == int(doc_id):
            continue
        else:
            recommendations.append({
                'id': doc['id'],
                'name': doc['name'],
                'price': doc['price'],
                'release_date': doc['release_date'],
                'path': doc['rec_path'],
                'tag_similarity': tag_similarity,
                'score_similarity': score_similarity,
                'overall_similarity': overall_similarity,
            })

    # Sort by overall similarity and take the top N results
    recommendations.sort(key=lambda x: -x['overall_similarity'])
    top_recommendations = recommendations[:top_n]

    # Convert to 2D vectors (x: tag similarity, y: score similarity)
    vectors = [{'x': rec['tag_similarity'], 'y': rec['score_similarity'], 'game': rec} for rec in top_recommendations]

    # Goal state (top 5 recommendation games [sorted] with its vector)
    return vectors
