from pydantic import BaseModel, field_validator
from typing import List

class ActivityVote(BaseModel):
    """Individual vote for a single activity."""
    user_id: int
    activity_id: int
    score: int  # Rating score (e.g., 1-5 stars, or 1-10)
    
    @field_validator('score')
    @classmethod
    def validate_score(cls, v):
        """Ensure score is between 1 and 10."""
        if not 1 <= v <= 10:
            raise ValueError('score must be between 1 and 10')
        return v


class Vote(BaseModel):
    """
    Simple voting: submit one or more activity votes.
    Each vote has a user_id, activity_id, and score (1-10).
    """
    votes: List[ActivityVote]
    
    @field_validator('votes')
    @classmethod
    def validate_no_duplicate_activities(cls, v):
        """Ensure user doesn't vote for the same activity twice."""
        activity_ids = [vote.activity_id for vote in v]
        if len(activity_ids) != len(set(activity_ids)):
            raise ValueError('Cannot vote for the same activity multiple times')
        return v
