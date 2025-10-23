from fastapi import APIRouter, Body
from typing import List
from app.models import ActivityVote

router = APIRouter()

@router.post("/vote", response_model=List[ActivityVote])
def vote_for_activities(votes: List[ActivityVote] = Body(...)):
    return votes
