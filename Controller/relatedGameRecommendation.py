from scipy.spatial.distance import euclidean
import numpy as np
from Controller import booleanQuerySteam


def calculate_similarity(target_tags, target_score, doc_tags, doc_score, weight_tags=0.7, weight_score=0.3):
    """Calculate weighted similarity based on tags and score."""
    # Tag similarity (Jaccard index)
    tag_similarity = len(set(target_tags) & set(doc_tags)) / len(set(target_tags) | set(doc_tags))

    # Score similarity (inverted normalized difference)
    score_similarity = 1 - abs(target_score - doc_score) / max(1, target_score, doc_score)

    # Weighted similarity
    overall_similarity = weight_tags * tag_similarity + weight_score * score_similarity
    return tag_similarity, score_similarity, overall_similarity


def recommend_related_games(target_game_tags, target_game_score, top_n=5):
    """Find and recommend related games."""
    # Perform a boolean search for documents with matching tags
    search_query = " OR ".join(target_game_tags)  # Example: "RPG OR Action OR Adventure"
    search_results = booleanQuerySteam.boolean_search(search_query)

    if not search_results:
        return []

    recommendations = []

    # Compare target game with search results
    for doc in search_results:
        doc_tags = booleanQuerySteam.inverted_index.get(doc['id'], {}).get("tags", [])
        doc_score = float(doc.get('review_no', 0))  # Assume `review_no` is the score

        # Calculate similarity
        tag_similarity, score_similarity, overall_similarity = calculate_similarity(
            target_tags=target_game_tags,
            target_score=target_game_score,
            doc_tags=doc_tags,
            doc_score=doc_score
        )

        recommendations.append({
            'id': doc['id'],
            'name': doc['name'],
            'price': doc['price'],
            'release_date': doc['release_date'],
            'path': doc['path'],
            'tag_similarity': tag_similarity,
            'score_similarity': score_similarity,
            'overall_similarity': overall_similarity
        })

    # Sort by overall similarity and take the top N results
    recommendations.sort(key=lambda x: -x['overall_similarity'])
    top_recommendations = recommendations[:top_n]

    # Convert to 2D vectors (x: tag similarity, y: score similarity)
    vectors = [{'x': rec['tag_similarity'], 'y': rec['score_similarity'], 'game': rec} for rec in top_recommendations]

    return vectors
