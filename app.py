from flask import Flask, render_template, redirect, url_for
import requests
import time

app = Flask(__name__)

API_KEY = "0caf5e3ed5mshb1a24b93a3df156p102bf1jsn5637a03a1e51"
BASE_URL ="https://cricbuzz-cricket.p.rapidapi.com"

HEADERS = {
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com",
    "x-rapidapi-key": API_KEY
}

# cache variables
cache_data = None
cache_time = 0
CACHE_DURATION = 120  # seconds


@app.route("/")
def home():
    return redirect(url_for('live_matches'))


@app.route("/live")
def live_matches():
    global cache_data, cache_time

    # check cache
    if cache_data and (time.time() - cache_time) < CACHE_DURATION:
        return render_template("live.html", matches=cache_data)

    url = f"{BASE_URL}/matches/v1/live"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 429:
        return "Rate limit exceeded. Please wait a few seconds.", 429

    if response.status_code != 200:
        return f"Error fetching live matches: {response.status_code}", 500

    data = response.json()
    live_matches = []

    for match_type in data.get("typeMatches", []):
        for series in match_type.get("seriesMatches", []):
            if "seriesAdWrapper" in series:
                series_info = series["seriesAdWrapper"]["seriesName"]

                for m in series["seriesAdWrapper"].get("matches", []):
                    info = m.get("matchInfo", {})
                    score = m.get("matchScore", {})

                    t1s = score.get("team1Score", {}).get("inngs1", {})
                    t2s = score.get("team2Score", {}).get("inngs1", {})

                    live_matches.append({
                        "match_id": info.get("matchId"),
                        "series": series_info,
                        "match_desc": info.get("matchDesc"),
                        "format": info.get("matchFormat"),
                        "team1": info.get("team1", {}).get("teamName"),
                        "team2": info.get("team2", {}).get("teamName"),
                        "t1_runs": t1s.get("runs"),
                        "t1_wkts": t1s.get("wickets"),
                        "t1_overs": t1s.get("overs"),
                        "t2_runs": t2s.get("runs"),
                        "t2_wkts": t2s.get("wickets"),
                        "t2_overs": t2s.get("overs"),
                        "status": info.get("status", "Live"),
                        "venue": info.get("venueInfo", {}).get("ground"),
                        "city": info.get("venueInfo", {}).get("city"),
                        "state": info.get("stateTitle", "")
                    })

    # update cache
    cache_data = live_matches
    cache_time = time.time()

    return render_template("live.html", matches=live_matches)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
