from strsimpy import overlap_coefficient

similarity_checker = overlap_coefficient.OverlapCoefficient()

def find_map(maps, map_name):
    similarity = [similarity_checker.similarity(m.lower(), map_name.lower()) for m in maps]
    max_score = max(similarity)
    if len([i for i in similarity if similarity == max_score]) > 1:
        return None

    for m, score in zip(maps, similarity):
        if score == max_score:
            return m