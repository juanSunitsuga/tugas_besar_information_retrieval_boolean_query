from Controller import booleanQuerySteam

def recommend_related_games(target_game_tags, target_game_cluster, top_n=5, doc_id=None):
    """Find and recommend related games based on cluster and tag similarity."""
    # Filter postings from the inverted index by target cluster
    same_cluster_docs = []
    for term, term_data in booleanQuerySteam.inverted_index.items():
        for doc_id_key, posting in term_data['postings'].items():
            if posting['cluster'] == target_game_cluster:

                if int(doc_id_key) not in [doc['id'] for doc in same_cluster_docs]:
                    same_cluster_docs.append({
                        'id': int(doc_id_key),
                        'cluster': posting['cluster']
                    })

    # If not found in the same cluster, return empty list
    if not same_cluster_docs:
        return []

    recommendations = []

    # Compare target game with documents in the same cluster
    for doc in same_cluster_docs:
        doc_id_current = doc['id']
        if doc_id_current == int(doc_id):  # Skip the target game itself
            continue

        # Retrieve document details
        doc_tags = booleanQuerySteam.document_data[doc_id_current]['data']['Tags']

        # Calculate similarity (Jaccard index)
        # Calculate the ratio of the overlapping tags to the overall tags
        tag_similarity = len(set(target_game_tags) & set(doc_tags)) / len(set(target_game_tags) | set(doc_tags))

        if doc['id'] == int(doc_id):
            continue
        else:
            recommendations.append({
                'id': doc['id'],
                'cluster': doc['cluster'],
                'name': booleanQuerySteam.document_data[doc['id']]['data']['Name'],
                'price': booleanQuerySteam.document_data[doc['id']]['data']['Price'],
                'release_date': booleanQuerySteam.document_data[doc['id']]['data']['Release_date'],
                'path': f"{booleanQuerySteam.document_data[doc['id']]['sanitized_name']}",
                'tag_similarity': tag_similarity
            })

    # Sort by tag similarity and take the top N results
    recommendations.sort(key=lambda x: -x['tag_similarity'])
    top_recommendations = recommendations[:top_n]

    recommended_game = [{'game': rec} for rec in top_recommendations]

    # Goal state (top 5 recommendation games [sorted])
    return recommended_game
