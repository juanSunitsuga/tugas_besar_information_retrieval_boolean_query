from Controller import booleanQuerySteam

#if needed : weight_tags=0.7, weight_score=0.3

def calculate_similarity(target_tags, target_cluster, doc_tags, doc_cluster, ):
    """Calculate weighted similarity based on tags and cluster."""
    tag_similarity =0

    # Cluster similarity (binary)
    if target_cluster == doc_cluster:
        # Tag similarity (Jaccard index)
        # Calculate the ratio of the overlapping tags to the overall tags
        tag_similarity = len(set(target_tags) & set(doc_tags)) / len(set(target_tags) | set(doc_tags))

        # Score similarity (inverted normalized difference)
        # Calculate the ratio of the difference price to the highest price
        # score_similarity = 1 - abs(target_price - doc_price) / max(1, target_price, doc_price)

    return  tag_similarity


def recommend_related_games(target_game_tags, target_game_cluster, top_n=5, doc_id=None):
    """Find and recommend related games."""
    # Perform a boolean search for documents with matching tags
    search_query = " OR ".join(target_game_tags)
    search_results = booleanQuerySteam.boolean_search(search_query)

    if not search_results:
        return []

    recommendations = []

    # Compare target game with search results
    for doc in search_results:
        doc_tags = doc['tags']
        doc_cluster = doc['cluster']
        # x = ''.join(c for c in doc.get('price', 0) if c in "1234567890.")
        # doc_price = float(0 if len(x) == 0 else x)

        # Exclude games with cluster = -1
        if doc_cluster == -1:
            continue

        # Calculate similarity
        tag_similarity = calculate_similarity(
            target_tags=target_game_tags,
            target_cluster=target_game_cluster,
            doc_tags=doc_tags,
            doc_cluster=doc_cluster,
        )

        if doc['id'] == int(doc_id):
            continue
        else:
            recommendations.append({
                'id': doc['id'],
                'score': doc['score'],
                'cluster': doc['cluster'],
                'name': doc['name'],
                'price': doc['price'],
                'release_date': doc['release_date'],
                'path': doc['rec_path'],
                'tag_similarity': tag_similarity
            })
            # 'score_similarity': score_similarity,
            # 'overall_similarity': overall_similarity

    # Sort by tag similarity and take the top N results
    recommendations.sort(key=lambda x: -x['tag_similarity'])
    top_recommendations = recommendations[:top_n]

    # Convert to 2D vectors (x: tag similarity, y: score similarity)
    vectors = [{'game': rec} for rec in top_recommendations]
    #'x': rec['tag_similarity'],'y': rec['score_similarity'],

    # Goal state (top 5 recommendation games [sorted] with its vector)
    return vectors
