from typing import List, Dict, Optional, Tuple
from datetime import date
from app.models.db.user import User
from app.models.db.activity import Activity, ActivityType
from app.services.user_service import get_user as get_user_dict
from app.services.vote_service import list_votes
import math
from collections import defaultdict


def calculate_user_similarity(user1: User, user2: User) -> float:
    """
    Calculate similarity score between two users based on their profiles and preferences.
    Returns a score between 0 (completely different) and 1 (very similar).
    """
    score = 0.0
    total_weight = 0.0

    weight = 3.0
    total_weight += weight
    if user1.interests and user2.interests:
        common_interests = set(user1.interests) & set(user2.interests)
        all_interests = set(user1.interests) | set(user2.interests)
        if all_interests:
            score += weight * (len(common_interests) / len(all_interests))

    weight = 2.0
    total_weight += weight
    if user1.birth_date and user2.birth_date:
        age1 = _calculate_age(user1.birth_date)
        age2 = _calculate_age(user2.birth_date)
        age_diff_ratio = 1 - min(
            abs(age1 - age2) / 20.0, 1.0
        ) 
        score += weight * age_diff_ratio

    weight = 1.5
    total_weight += weight
    if user1.city and user2.city:
        if user1.city.lower() == user2.city.lower():
            score += weight
        elif (
            user1.country
            and user2.country
            and user1.country.lower() == user2.country.lower()
        ):
            score += weight * 0.5

    weight = 1.0
    total_weight += weight
    if user1.activity_preference and user2.activity_preference:
        if user1.activity_preference == user2.activity_preference:
            score += weight
        elif "either" in (user1.activity_preference, user2.activity_preference):
            score += weight * 0.5

    weight = 0.5
    total_weight += weight
    if user1.gender and user2.gender and user1.gender == user2.gender:
        score += weight

    return score / total_weight if total_weight > 0 else 0.0


def _calculate_age(birth_date: date) -> int:
    """Calculate age from birth date."""
    today = date.today()
    return (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )


def get_user_activity_preferences(user_id: int) -> Dict[int, float]:
    """
    Build a preference profile for a user based on their voting history.
    Returns a dictionary mapping activity IDs to preference scores.
    """
    votes = list_votes()
    print("All votes: ", votes)
    preferences = {}
    total_activities = 0

    user_votes = [v for v in votes if v.get("user_id") == user_id]

    for vote in user_votes:
        ranking = vote.get("activity_ranking", [])
        total_activities = max(total_activities, len(ranking))

        for position, activity_id in enumerate(ranking):
            score = (len(ranking) - position) / len(ranking)
            if activity_id in preferences:
                preferences[activity_id] = max(preferences[activity_id], score)
            else:
                preferences[activity_id] = score

    return preferences


def find_similar_users(
    user: User, min_similarity: float = 0.3
) -> List[Tuple[User, float]]:
    """
    Find users similar to the given user.
    Returns list of (user, similarity_score) tuples sorted by similarity.
    """
    similar_users = []

    user_dicts = [get_user_dict(i) for i in range(1, 6) if i != user.id]
    test_users = [User(**u) if u else None for u in user_dicts]
    test_users = [u for u in test_users if u is not None]  # Remove None values
    print("Comparing user id:", user.id, "with test users:", [u.id for u in test_users])
    for other_user in test_users:
        if other_user and other_user.id != user.id:
            similarity = calculate_user_similarity(user, other_user)
            print("Similarity between user", user.id, "and user", other_user.id, ":", similarity)
            if similarity >= min_similarity:
                similar_users.append((other_user, similarity))
                print("similar_users: ", similar_users)

    return similar_users


def get_collaborative_recommendations(
    user: User, current_activities: List[Activity], max_recommendations: int = 5
) -> List[Tuple[Activity, float]]:
    """
    Get activity recommendations based on similar users' preferences.
    Returns list of (activity, score) tuples sorted by score.
    """
    similar_users = find_similar_users(user)
    if not similar_users:
        print("-----------------> No similar users found for user id:", user.id)
        return []
    all_preferences = {}
    for similar_user, similarity in similar_users:
        user_prefs = get_user_activity_preferences(similar_user.id)
        print("user_prefs: ", user_prefs)
        for activity_id, score in user_prefs.items():
            weighted_score = score * similarity
            if activity_id in all_preferences:
                all_preferences[activity_id] = max(
                    all_preferences[activity_id], weighted_score
                )
            else:
                all_preferences[activity_id] = weighted_score

    scored_activities = []
    for activity in current_activities:
        base_score = all_preferences.get(activity.id, 0.0)

        if user.interests and activity.type:
            interest_match = any(
                interest.lower() in str(activity.type).lower()
                for interest in user.interests
            )
            if interest_match:
                base_score *= 1.2

        if user.activity_preference != "either":
            if (user.activity_preference == "indoor" and activity.is_indoor) or (
                user.activity_preference == "outdoor" and not activity.is_indoor
            ):
                base_score *= 1.1

        if base_score > 0:
            scored_activities.append((activity, base_score))

    scored_activities.sort(key=lambda x: x[1], reverse=True)
    return scored_activities[:max_recommendations]
