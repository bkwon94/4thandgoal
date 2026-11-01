"""
The rank score of a value inside its group: 1 for the highest, 0 for the lowest.
The waiver engine and the waiver buckets both rank on it, so it lives apart from both.
"""


def rank_scores(positions: dict[str, str], values: dict[str, float]) -> dict[str, float]:
    """The rank score of each key: the rank of its value inside its group, from 1 for the highest to 0.

    The group is the position for a player and one group for every team. Keys with the same value share the
    better rank.
    """
    by_position: dict[str, list[float]] = {}
    for pid, position in positions.items():
        by_position.setdefault(position, []).append(values[pid])
    for ranked in by_position.values():
        ranked.sort(reverse=True)
    scores = {}
    for pid, position in positions.items():
        ranked = by_position[position]
        ahead_of = ranked.index(values[pid])
        scores[pid] = 1.0 if len(ranked) == 1 else round(1 - ahead_of / (len(ranked) - 1), 4)
    return scores
