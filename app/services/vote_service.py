from typing import List, Dict
from threading import Lock

_LOCK = Lock()
_VOTES: List[Dict] = []  # list of vote dicts: {"user_id": int, "activity_id": int, "score": int}


def reset_votes() -> None:
    """Clear in-memory votes."""
    with _LOCK:
        _VOTES.clear()


def add_vote(vote: Dict) -> None:
    print("Adding vote:", vote)
    """Add a single activity vote."""
    with _LOCK:
        _VOTES.append(vote.copy())


def list_votes() -> List[Dict]:
    """Get all votes."""
    with _LOCK:
        return [v.copy() for v in _VOTES]


def get_votes_for_activity(activity_id: int) -> List[Dict]:
    """Get all votes for a specific activity."""
    with _LOCK:
        return [v.copy() for v in _VOTES if v.get("activity_id") == activity_id]


def get_activity_ranking() -> List[Dict]:
    """
    Get activities ranked by average score.
    Returns list of {activity_id, average_score, vote_count} sorted by score desc.
    """
    with _LOCK:
        votes = [v.copy() for v in _VOTES]
    
    # Group by activity
    activity_scores = {}
    for v in votes:
        aid = v.get("activity_id")
        score = v.get("score")
        if aid not in activity_scores:
            activity_scores[aid] = []
        activity_scores[aid].append(score)
    
    # Calculate averages
    ranking = []
    for aid, scores in activity_scores.items():
        avg = sum(scores) / len(scores)
        ranking.append({
            "activity_id": aid,
            "average_score": round(avg, 2),
            "vote_count": len(scores)
        })
    
    # Sort by average score descending
    ranking.sort(key=lambda x: x["average_score"], reverse=True)
    return ranking
