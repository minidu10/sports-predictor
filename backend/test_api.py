import requests
import json

BASE = 'http://localhost:5000'

def test(label, method, url, payload=None):
    try:
        resp = method(url, json=payload, timeout=5)
        print(f"\n{'='*50}")
        print(f"TEST: {label}")
        print(f"Status: {resp.status_code}")
        print(json.dumps(resp.json(), indent=2))
    except Exception as e:
        print(f"FAILED: {label} — {e}")

# Health check
test("Health", requests.get, f"{BASE}/health")

# Cricket — valid
test("Cricket valid prediction", requests.post, f"{BASE}/api/predict/cricket", {
    "team1": "India",
    "team2": "Australia",
    "inn1_runs": 287,
    "inn1_wickets": 6,
    "inn1_balls": 300
})

# Cricket — missing field
test("Cricket missing field", requests.post, f"{BASE}/api/predict/cricket", {
    "team1": "India",
    "team2": "Australia"
})

# Cricket — unknown team
test("Cricket unknown team", requests.post, f"{BASE}/api/predict/cricket", {
    "team1": "Unknown FC",
    "team2": "Australia",
    "inn1_runs": 200,
    "inn1_wickets": 5,
    "inn1_balls": 300
})

# Football — valid
test("Football valid prediction", requests.post, f"{BASE}/api/predict/football", {
    "home_team": "Arsenal FC",
    "away_team": "Chelsea FC",
    "matchday": 10
})

# Football — missing field
test("Football missing field", requests.post, f"{BASE}/api/predict/football", {
    "home_team": "Arsenal FC"
})

# Football — unknown team
test("Football unknown team", requests.post, f"{BASE}/api/predict/football", {
    "home_team": "Fake United",
    "away_team": "Chelsea FC",
    "matchday": 5
})
