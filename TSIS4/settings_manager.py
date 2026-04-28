import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

DEFAULT_SETTINGS = {
    "snake_color": [0, 200, 0],
    "grid_overlay": True,
    "sound": True,
}


def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
        merged = {**DEFAULT_SETTINGS, **data}
        merged["snake_color"] = [int(c) for c in merged["snake_color"]]
        return merged
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)
