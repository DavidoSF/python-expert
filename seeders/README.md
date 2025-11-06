# Seeders

This directory contains seeder scripts for populating the application with sample data for testing and development.

## Available Seeders

### `seed_activities_and_votes.py`

Creates sample activities and votes for testing the voting and activity recommendation system.

**What it creates:**
- 4 sample activities in Paris:
  - 🎵 **Paris Jazz Night** (Cultural, Indoor) - ID: 100
  - 🧘 **Outdoor Yoga in Jardin du Luxembourg** (Sports, Outdoor) - ID: 101
  - 🛒 **Community Food Market** (Community, Outdoor) - ID: 102
  - 🎬 **Cinema Classics: French New Wave** (Cultural, Indoor) - ID: 103

- Votes from existing users (users 1-4) with realistic scoring patterns based on their profiles

**Usage:**

```bash
# Run the seeder
python seeders/seed_activities_and_votes.py
```

**Output:**
- Creates activities in the `admin_activities` list (in-memory)
- Creates votes in the `vote_service._VOTES` store (in-memory)
- Displays ranking and vote statistics

**Note:** 
- Data is stored in memory only and will be cleared when the application restarts
- Make sure users exist in `app/data/users.json` before running
- The seeder uses realistic voting patterns based on user interests and preferences

## Testing the Seeded Data

After running the seeder, you can test the data through the API:

```bash
# View all admin activities
curl http://localhost:8000/admin/activities

# View activity ranking
curl http://localhost:8000/vote/ranking

# View votes for a specific activity
curl http://localhost:8000/vote/activity/100

# Get all votes
curl http://localhost:8000/vote/

# Get activities filtered by weather and ordered by votes
curl "http://localhost:8000/activities/by-votes?city=Paris&countryCode=FR&date=2025-11-15"
```

## Creating Custom Seeders

To create a new seeder:

1. Create a new Python file in the `seeders/` directory
2. Import necessary models and services
3. Add seed data creation logic
4. Run with `python seeders/your_seeder.py`

Example structure:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.db.activity import Activity, ActivityType
from app.routes.admin import admin_activities

def seed_data():
    # Your seeding logic here
    pass

if __name__ == "__main__":
    seed_data()
```

## Data Persistence

**Important:** All seeded data is stored in memory and will be lost when:
- The application server restarts
- The seeder script completes (data only persists if the server is already running)

For persistent data, you would need to:
- Implement a database backend
- Or manually add data to the JSON files in `app/data/`
