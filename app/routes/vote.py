from fastapi import APIRouter, Body, HTTPException
from typing import List, Dict
from app.models.db.vote import Vote, ActivityVote
from app.services import vote_service
from app.services import activity_lookup_service

router = APIRouter(prefix="/vote", tags=["vote"])


@router.post("/", status_code=201)
def submit_vote(vote: Vote = Body(...)):
    """
    Submit votes for one or more activities.
    
    Example:
    {
      "votes": [
        {"user_id": 1, "activity_id": 5, "score": 9},
        {"user_id": 1, "activity_id": 3, "score": 7}
      ]
    }
    
    Score range: 1-10 (10 = best)
    Cannot vote for the same activity twice in one submission.
    Activities must exist (admin activities only for now).
    """
    if not vote.votes:
        raise HTTPException(status_code=400, detail="votes list cannot be empty")
    
    # Validate that all activities exist
    for activity_vote in vote.votes:
        if not activity_lookup_service.activity_exists(activity_vote.activity_id):
            raise HTTPException(
                status_code=404, 
                detail=f"Activity with id {activity_vote.activity_id} does not exist"
            )
    
    # Store each vote
    for activity_vote in vote.votes:
        vote_service.add_vote(activity_vote.model_dump())
    
    return {"status": "ok", "votes_recorded": len(vote.votes)}


@router.get("/", response_model=List[Dict])
def list_votes():
    """List all recorded votes."""
    return vote_service.list_votes()


@router.get("/activity/{activity_id}")
def get_activity_votes(activity_id: int):
    """Get all votes for a specific activity with average score."""
    votes = vote_service.get_votes_for_activity(activity_id)
    if not votes:
        return {"activity_id": activity_id, "votes": [], "average_score": 0, "total_votes": 0}
    
    avg_score = sum(v["score"] for v in votes) / len(votes)
    return {
        "activity_id": activity_id,
        "votes": votes,
        "average_score": round(avg_score, 2),
        "total_votes": len(votes)
    }


@router.get("/ranking")
def get_activity_ranking():
    """Get activities ranked by average score."""
    return vote_service.get_activity_ranking()
