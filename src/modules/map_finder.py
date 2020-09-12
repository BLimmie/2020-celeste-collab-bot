from strsimpy import overlap_coefficient

similarity_checker = overlap_coefficient.OverlapCoefficient()

def find_closest(search, target):
    similarity = [similarity_checker.similarity(m.lower(), target.lower()) for m in search]
    max_score = max(similarity)
    if len([i for i in similarity if similarity == max_score]) > 1:
        return None, None
    print(search, similarity)
    for m, score in zip(search, similarity):
        if score == max_score:
            return m, max_score

def find_map (maps, map_name):
    return find_closest(maps, map_name)

def find_label(label):
    labels = ["Bug", "Gameplay", "Speedrun", "Visual", "Accessibility", "Other"]
    l, score = find_closest(labels, label)
    if score < 0.5:
        return "Other"
    else:
        return l
