from typing import List, Dict, Optional
from threading import Lock
from app.models.db.vote import Vote

_LOCK = Lock()
_VOTES: List[Dict] = []  # list of vote dicts


def reset_votes() -> None:
    """Clear in-memory votes."""
    with _LOCK:
        _VOTES.clear()


def add_vote(vote: Dict) -> None:
    """Add a vote (expects dict with 'user_id' and 'activity_ranking' list of ids)."""
    with _LOCK:
        _VOTES.append(vote.copy())


def list_votes() -> List[Dict]:
    with _LOCK:
        return [v.copy() for v in _VOTES]


def _pairwise_counts(candidates: List[int]) -> Dict[int, Dict[int, int]]:
    """Return nested dict counts[a][b] = number of voters preferring a over b."""
    counts = {a: {b: 0 for b in candidates if b != a} for a in candidates}
    with _LOCK:
        votes = [v.copy() for v in _VOTES]
    for v in votes:
        ranking = v.get("activity_ranking", [])
        # Build a position map: activity_id -> position (lower is more preferred)
        pos = {aid: idx for idx, aid in enumerate(ranking)}
        for a in candidates:
            for b in candidates:
                if a == b:
                    continue
                pa = pos.get(a, None)
                pb = pos.get(b, None)
                # If a appears and b not, prefer a. If both appear, compare positions.
                if pa is not None and pb is None:
                    counts[a][b] += 1
                elif pa is None and pb is not None:
                    # prefer b, so a does not get a vote
                    pass
                elif pa is not None and pb is not None:
                    if pa < pb:
                        counts[a][b] += 1
                else:
                    # neither ranked: no preference
                    pass
    return counts


def condorcet_ranking(candidates: List[int]) -> Dict:
    """Compute Condorcet pairwise results and return ranking info.

    Returns a dict with:
      - 'pairwise': counts dict
      - 'winner': candidate id if Condorcet winner exists else None
      - 'copeland': list of tuples (candidate, score) sorted desc
    """
    counts = _pairwise_counts(candidates)
    # Determine pairwise wins
    wins = {a: 0 for a in candidates}
    losses = {a: 0 for a in candidates}
    for a in candidates:
        for b in candidates:
            if a == b:
                continue
            a_over_b = counts[a].get(b, 0)
            b_over_a = counts[b].get(a, 0)
            if a_over_b > b_over_a:
                wins[a] += 1
            elif a_over_b < b_over_a:
                losses[a] += 1
            else:
                # tie => no increment
                pass
    # Condorcet winner: candidate that beats every other (wins == n-1)
    n = len(candidates)
    winner = None
    for a in candidates:
        if wins[a] == n - 1:
            winner = a
            break
    # Copeland score: wins - losses
    copeland = [(a, wins[a] - losses[a]) for a in candidates]
    copeland.sort(key=lambda x: x[1], reverse=True)
    return {"pairwise": counts, "winner": winner, "copeland": copeland}


# Convenience: compute ranking from stored votes across all candidates found in votes
def ranking_from_votes() -> Dict:
    with _LOCK:
        votes = [v.copy() for v in _VOTES]
    # collect candidate ids
    candidates = set()
    for v in votes:
        for aid in v.get("activity_ranking", []):
            candidates.add(aid)
    candidates = list(candidates)
    return condorcet_ranking(candidates)
