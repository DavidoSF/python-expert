from fastapi import APIRouter, Body, HTTPException
from typing import List, Dict
from app.models.db.vote import Vote
from app.services import vote_service

router = APIRouter(prefix="/vote", tags=["vote"])


@router.post("/", status_code=201)
def submit_vote(vote: Vote = Body(...)):
    """Submit a user's ranked list of activity ids (highest preference first)."""
    # Basic validation: ensure activity_ranking is non-empty
    if not vote.activity_ranking:
        raise HTTPException(status_code=400, detail="activity_ranking must be a non-empty list of activity ids")
    vote_dict = vote.dict()
    vote_service.add_vote(vote_dict)
    return {"status": "ok"}


@router.get("/", response_model=List[Dict])
def list_votes():
    return vote_service.list_votes()


@router.get("/result")
def vote_result():
    """Compute Condorcet results across stored votes and return ranking info."""
    result = vote_service.ranking_from_votes()
    return result
