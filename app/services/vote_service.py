from typing import List, Dict, Optional, Set, Tuple
from threading import Lock
from pathlib import Path
import json
from app.models.db.vote import Vote
from collections import defaultdict

_LOCK = Lock()
_VOTES: List[Dict] = []

VOTES_FILE = Path(__file__).resolve().parents[1] / "data" / "votes.json"

def _load_votes_from_file():
    """Load votes from JSON file if it exists."""
    global _VOTES
    if VOTES_FILE.exists():
        try:
            with open(VOTES_FILE, 'r', encoding='utf-8') as f:
                votes_data = json.load(f)
                with _LOCK:
                    _VOTES.clear()
                    _VOTES.extend(votes_data)
                print(f"Loaded {len(_VOTES)} votes from {VOTES_FILE}")
        except Exception as e:
            print(f"Error loading votes from file: {e}")

_load_votes_from_file()

class VoteService:
    def __init__(self):
        self.votes: List[Dict] = []
        self.candidates: Set[int] = set()
        self.pairwise_counts: Dict[int, Dict[int, int]] = {}
        self.strongest_paths: Dict[int, Dict[int, int]] = {}
    
    def parse(self, votes_data: List[Dict]) -> None:
        """
        Parse vote data and build the initial data structures.
        
        Args:
            votes_data: List of vote dictionaries with 'user_id' and 'activity_ranking'
        """
        self.votes = votes_data
        self.candidates = set()
        
        for vote in votes_data:
            ranking = vote.get('activity_ranking', [])
            self.candidates.update(ranking)
    
    def score(self) -> None:
        """
        Compute pairwise comparisons between all candidates using the Condorcet method.
        Creates a matrix of how many times each candidate was preferred over each other.
        """
        candidates = list(self.candidates)
        self.pairwise_counts = {
            a: {b: 0 for b in candidates if b != a}
            for a in candidates
        }
        
        for vote in self.votes:
            ranking = vote.get('activity_ranking', [])
            pos = {aid: idx for idx, aid in enumerate(ranking)}
            
            for i, a in enumerate(candidates):
                for b in candidates[i+1:]:
                    if a == b:
                        continue
                        
                    pos_a = pos.get(a)
                    pos_b = pos.get(b)
                    
                    if pos_a is not None and pos_b is not None:
                        if pos_a < pos_b: 
                            self.pairwise_counts[a][b] += 1
                        else:  
                            self.pairwise_counts[b][a] += 1
                    elif pos_a is not None:  
                        self.pairwise_counts[a][b] += 1
                    elif pos_b is not None: 
                        self.pairwise_counts[b][a] += 1
    
    def build_graph(self) -> None:
        """
        Build the directed graph of strongest paths between candidates using the Schulze method.
        For each pair of candidates, finds the strongest path (maximum minimum strength along path).
        """
        candidates = list(self.candidates)
        
        self.strongest_paths = {
            a: {b: self.pairwise_counts[a].get(b, 0) for b in candidates if b != a}
            for a in candidates
        }
        
        for k in candidates:
            for i in candidates:
                if i == k:
                    continue
                for j in candidates:
                    if j == k or j == i:
                        continue
                    
                    current = self.strongest_paths[i].get(j, 0)
                    path_i_k = self.strongest_paths[i].get(k, 0)
                    path_k_j = self.strongest_paths[k].get(j, 0)
                    
                    path_strength = min(path_i_k, path_k_j)
                    
                    if path_strength > current:
                        self.strongest_paths[i][j] = path_strength
    
    def order_votes(self) -> List[int]:
        """
        Determine the final ranking using the Schulze method.
        Returns ordered list of candidate IDs from winner to loser.
        
        Returns:
            List[int]: Ordered list of candidate IDs
        """
        candidates = list(self.candidates)
        
        wins = defaultdict(int)
        for i in candidates:
            for j in candidates:
                if i == j:
                    continue
                if self.strongest_paths[i].get(j, 0) > self.strongest_paths[j].get(i, 0):
                    wins[i] += 1
        
        ranked = sorted(candidates, key=lambda x: wins[x], reverse=True)
        return ranked


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


def get_activity_votes(activity_id: int) -> List[Dict]:
    """
    Get all votes for a specific activity.
    
    Args:
        activity_id: The ID of the activity to get votes for
        
    Returns:
        List of vote dictionaries for the specified activity.
        Returns empty list if no votes exist for this activity.
    """
    with _LOCK:
        return [v.copy() for v in _VOTES if v.get("activity_id") == activity_id]


def get_activity_ranking() -> List[Dict]:
    """
    Get activities ranked by average score.
    Returns list of {activity_id, average_score, vote_count} sorted by score desc.
    """
    with _LOCK:
        votes = [v.copy() for v in _VOTES]
    
    activity_scores = {}
    for v in votes:
        aid = v.get("activity_id")
        score = v.get("score")
        if aid not in activity_scores:
            activity_scores[aid] = []
        activity_scores[aid].append(score)
    
    ranking = []
    for aid, scores in activity_scores.items():
        avg = sum(scores) / len(scores)
        ranking.append({
            "activity_id": aid,
            "average_score": round(avg, 2),
            "vote_count": len(scores)
        })
    
    ranking.sort(key=lambda x: x["average_score"], reverse=True)
    return ranking
