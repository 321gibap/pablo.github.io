import requests
import json
import os
from datetime import datetime

# Exchange refresh token for a fresh access token
def get_access_token():
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": os.environ["STRAVA_CLIENT_ID"],
            "client_secret": os.environ["STRAVA_CLIENT_SECRET"],
            "refresh_token": os.environ["STRAVA_REFRESH_TOKEN"],
            "grant_type": "refresh_token",
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]

# Fetch all activities (paginated)
def fetch_activities(access_token):
    activities = []
    page = 1
    while True:
        response = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"per_page": 100, "page": page},
        )
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        activities.extend(batch)
        page += 1
    return activities

def main():
    print("Fetching access token...")
    token = get_access_token()

    print("Fetching activities...")
    activities = fetch_activities(token)
    print(f"  → {len(activities)} activities found")

    # Save raw data
    os.makedirs("data", exist_ok=True)
    with open("data/activities.json", "w") as f:
        json.dump(activities, f, indent=2)

    # Save a lightweight summary (useful for fast-loading charts later)
    summary = [
        {
            "id": a["id"],
            "name": a["name"],
            "type": a["type"],
            "date": a["start_date_local"],
            "distance_m": a["distance"],
            "moving_time_s": a["moving_time"],
            "elevation_m": a["total_elevation_gain"],
            "map_polyline": a.get("map", {}).get("summary_polyline"),
        }
        for a in activities
    ]
    with open("data/summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Saved data/activities.json and data/summary.json")
    print(f"Last updated: {datetime.utcnow().isoformat()}Z")

if __name__ == "__main__":
    main()
