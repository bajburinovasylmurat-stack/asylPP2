"""persistence.py — Load/save leaderboard.json and settings.json"""

import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

DEFAULT_SETTINGS = {
    "sound":       False,
    "car_color":   [0, 200, 255],
    "difficulty":  "normal",  
    "username":    "",
}

DIFFICULTY_PARAMS = {
    "easy":   {"traffic_density": 0.4, "obstacle_freq": 0.3, "coin_value_mult": 1.2},
    "normal": {"traffic_density": 1.0, "obstacle_freq": 1.0, "coin_value_mult": 1.0},
    "hard":   {"traffic_density": 1.8, "obstacle_freq": 1.8, "coin_value_mult": 0.8},
}



def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
            merged = DEFAULT_SETTINGS.copy()
            merged.update(data)
            return merged
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print("Could not save settings:", e)



def load_leaderboard() -> list:
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []


def save_leaderboard(entries: list) -> None:
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(entries, f, indent=2)
    except Exception as e:
        print("Could not save leaderboard:", e)


def add_score(username: str, score: int, distance: int, coins: int) -> list:
    """Add a new entry and return the updated top-10 list."""
    entries = load_leaderboard()
    entries.append({
        "rank":     0,
        "name":     username,
        "score":    score,
        "distance": distance,
        "coins":    coins,
    })
    entries.sort(key=lambda e: e["score"], reverse=True)
    entries = entries[:10]
    for i, e in enumerate(entries):
        e["rank"] = i + 1
    save_leaderboard(entries)
    return entries