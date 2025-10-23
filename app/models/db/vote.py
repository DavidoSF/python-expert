from pydantic import BaseModel
from typing import List, Optional
from app.models.db.activity import ActivityVote

class Vote(BaseModel):
    user_id: int
    activity_ranking: List[int]
    activity_scores: Optional[List[ActivityVote]] = None
