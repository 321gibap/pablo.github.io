import fs from "fs";
import fetch from "node-fetch";

const STRAVA_API_URL = "https://www.strava.com/api/v3";

async function refreshAccessToken() {
  const res = await fetch(`${STRAVA_API_URL}/oauth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      client_id: process.env.STRAVA_CLIENT_ID,
      client_secret: process.env.STRAVA_CLIENT_SECRET,
      refresh_token: process.env.STRAVA_REFRESH_TOKEN,
      grant_type: "refresh_token"
    }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(`Failed to refresh token: ${JSON.stringify(data)}`);
  return data.access_token;
}

async function fetchActivities(token) {
  const res = await fetch(`${STRAVA_API_URL}/athlete/activities?per_page=10`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(`Failed to fetch activities: ${JSON.stringify(data)}`);
  return data;
}

async function main() {
  const token = await refreshAccessToken();
  const activities = await fetchActivities(token);

  const simplified = activities.map(a => ({
    name: a.name,
    distance_m: a.distance,
    start_date: a.start_date_local,
    type: a.type,
    map: a.map.summary_polyline
  }));

  // Ensure directory exists
  fs.mkdirSync("data", { recursive: true });

  fs.writeFileSync("data/activities.json", JSON.stringify(simplified, null, 2));
  console.log(`✅ Updated ${simplified.length} activities.`);
}

main().catch(err => {
  console.error("❌ Error updating activities:", err);
  process.exit(1);
});
