"""
Seeder script to create sample activities and votes for testing.
This script creates 3-4 activities and has existing users vote on them.
Saves data to JSON files for persistence.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.routes.admin import admin_activities
from app.models.db.activity import Activity, ActivityType
from app.services import vote_service
from app.services import user_service

DATA_DIR = Path(__file__).resolve().parents[1] / "app" / "data"
ACTIVITIES_FILE = DATA_DIR / "activities.json"
VOTES_FILE = DATA_DIR / "votes.json"


def seed_activities():
    """Create sample activities in the admin_activities list."""
    print("Seeding activities...")

    admin_activities.clear()

    sample_activities = [
        Activity(
            id=100,
            name="Paris Jazz Night",
            description="Live jazz performance at La Seine Musicale featuring local and international artists",
            date="2025-11-15T20:00:00",
            location="Paris",
            type=ActivityType.cultural,
            is_indoor=True,
        ),
        Activity(
            id=101,
            name="Outdoor Yoga in Jardin du Luxembourg",
            description="Morning yoga session in the beautiful Luxembourg Gardens. All levels welcome!",
            date="2025-11-15T08:00:00",
            location="Paris",
            type=ActivityType.sports,
            is_indoor=False,
        ),
        Activity(
            id=102,
            name="Community Food Market",
            description="Local farmers and artisans market with fresh produce, crafts, and street food",
            date="2025-11-15T10:00:00",
            location="Paris",
            type=ActivityType.community,
            is_indoor=False,
        ),
        Activity(
            id=103,
            name="Cinema Classics: French New Wave",
            description="Screening of classic French cinema at Le Champo. This week: 'Breathless' by Godard",
            date="2025-11-15T19:30:00",
            location="Paris",
            type=ActivityType.cultural,
            is_indoor=True,
        ),
    ]

    for activity in sample_activities:
        admin_activities.append(activity)
    print(f"Created {len(sample_activities)} activities:")
    for activity in sample_activities:
        print(
            f"   - [{activity.id}] {activity.name} ({activity.type.value}, {'indoor' if activity.is_indoor else 'outdoor'})"
        )

    activities_data = [activity.model_dump() for activity in sample_activities]
    with open(ACTIVITIES_FILE, "w", encoding="utf-8") as f:
        json.dump(activities_data, f, indent=2, ensure_ascii=False)
    print(f"Saved activities to {ACTIVITIES_FILE}")

    return sample_activities


def seed_votes():
    """Have existing users vote on the activities."""
    print("\nSeeding votes...")

    vote_service._VOTES.clear()

    user_service._ensure_loaded()
    users = user_service.list_users()

    if not users:
        print("No users found. Please ensure users exist before running seeder.")
        return

    print(f"Found {len(users)} users")

    vote_patterns = {
        1: {
            100: 10,
            101: 6,
            102: 7,
            103: 9,
        },
        2: {
            100: 9,
            101: 7,
            102: 10,
            103: 8,
        },
        3: {
            100: 7,
            101: 8,
            102: 6,
            103: 7,
        },
        4: {
            100: 8,
            101: 9,
            102: 9,
            103: 6,
        },
    }

    vote_count = 0
    for user_id, votes in vote_patterns.items():

        user = user_service.get_user_by_id(user_id)
        if not user:
            print(f"User {user_id} not found, skipping votes")
            continue

        for activity_id, score in votes.items():
            vote_data = {"user_id": user_id, "activity_id": activity_id, "score": score}
            vote_service.add_vote(vote_data)
            vote_count += 1

    print(f"Created {vote_count} votes")

    all_votes = vote_service.list_votes()
    with open(VOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(all_votes, f, indent=2, ensure_ascii=False)
    print(f"Saved votes to {VOTES_FILE}")

    print("\nVote Summary:")
    activity_scores = {}

    for vote in all_votes:
        activity_id = vote["activity_id"]
        score = vote["score"]
        if activity_id not in activity_scores:
            activity_scores[activity_id] = []
        activity_scores[activity_id].append(score)

    for activity in admin_activities:
        if activity.id in activity_scores:
            scores = activity_scores[activity.id]
            avg_score = sum(scores) / len(scores)
            print(f"   - [{activity.id}] {activity.name}")
            print(f"     Average Score: {avg_score:.1f}/10 ({len(scores)} votes)")
            print(f"     Individual Scores: {scores}")


def show_ranking():
    """Display the activity ranking."""
    print("\nActivity Ranking:")
    ranking = vote_service.get_activity_ranking()

    for i, rank in enumerate(ranking, 1):
        activity = next(
            (a for a in admin_activities if a.id == rank["activity_id"]), None
        )
        if activity:
            print(f"   {i}. {activity.name}")
            print(
                f"      Score: {rank['average_score']:.1f}/10 ({rank['vote_count']} votes)"
            )


def main():
    """Main seeder function."""
    print("=" * 60)
    print("ACTIVITY & VOTE SEEDER")
    print("=" * 60)

    activities = seed_activities()
    seed_votes()
    show_ranking()

    print("\n" + "=" * 60)
    print("Seeding complete!")


if __name__ == "__main__":
    main()
