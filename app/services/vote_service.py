from typing import List, Dict, Optional, Set, Tuple
from threading import Lock
from app.models.db.vote import Vote
from collections import defaultdict

_LOCK = Lock()
_VOTES: List[Dict] = []  # list of vote dicts

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
        
        # Extract all candidates from rankings
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
            # Convert ranking to preference dictionary (activity_id -> position)
            pos = {aid: idx for idx, aid in enumerate(ranking)}
            
            # For each pair of candidates
            for i, a in enumerate(candidates):
                for b in candidates[i+1:]:
                    if a == b:
                        continue
                        
                    pos_a = pos.get(a)
                    pos_b = pos.get(b)
                    
                    # Compare positions to determine preference
                    if pos_a is not None and pos_b is not None:
                        if pos_a < pos_b:  # a is preferred over b
                            self.pairwise_counts[a][b] += 1
                        else:  # b is preferred over a
                            self.pairwise_counts[b][a] += 1
                    elif pos_a is not None:  # only a appears in ranking
                        self.pairwise_counts[a][b] += 1
                    elif pos_b is not None:  # only b appears in ranking
                        self.pairwise_counts[b][a] += 1
    
    def build_graph(self) -> None:
        """
        Build the directed graph of strongest paths between candidates using the Schulze method.
        For each pair of candidates, finds the strongest path (maximum minimum strength along path).
        """
        candidates = list(self.candidates)
        
        # Initialize strongest paths with direct pairwise counts
        self.strongest_paths = {
            a: {b: self.pairwise_counts[a].get(b, 0) for b in candidates if b != a}
            for a in candidates
        }
        
        # Floyd-Warshall algorithm to find strongest paths
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
                    
                    # The strength of the path i->k->j is the minimum of the two segments
                    path_strength = min(path_i_k, path_k_j)
                    
                    # Update if the new path is stronger
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
        
        # For each candidate, count how many others they beat
        wins = defaultdict(int)
        for i in candidates:
            for j in candidates:
                if i == j:
                    continue
                # i beats j if the strongest path i->j is stronger than j->i
                if self.strongest_paths[i].get(j, 0) > self.strongest_paths[j].get(i, 0):
                    wins[i] += 1
        
        # Sort candidates by number of wins (descending)
        ranked = sorted(candidates, key=lambda x: wins[x], reverse=True)
        return ranked


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


def compute_rankings() -> List[int]:
    """
    Compute the Condorcet/Schulze ranking for all current votes.
    Returns ordered list of activity IDs from most to least preferred.
    """
    with _LOCK:
        votes = [v.copy() for v in _VOTES]
    
    vote_service = VoteService()
    vote_service.parse(votes)
    vote_service.score()
    vote_service.build_graph()
    return vote_service.order_votes()


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
