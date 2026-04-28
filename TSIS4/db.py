import json
import urllib.request
import urllib.error
from config import SUPABASE_URL, SUPABASE_ANON_KEY

API_BASE = f"{SUPABASE_URL}/functions/v1/snake-api"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "apikey": SUPABASE_ANON_KEY,
}


def _request(method, path, data=None, params=None):
    url = f"{API_BASE}/{path}"
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        url += f"?{query}"

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.URLError:
        return None
    except Exception:
        return None


def save_score(username, score, level_reached):
    return _request("POST", "save", {
        "username": username,
        "score": score,
        "level_reached": level_reached,
    })


def get_leaderboard():
    result = _request("GET", "leaderboard")
    return result if isinstance(result, list) else []


def get_personal_best(username):
    result = _request("GET", "personal-best", params={"username": username})
    if result and "best_score" in result:
        return result["best_score"]
    return None
