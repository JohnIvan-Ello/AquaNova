import json, os, config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WAYPOINTS_FILE = os.path.join(BASE_DIR, "waypoints.json")

def load_waypoints():
    """Load waypoints from file (return dict)."""
    if not os.path.exists(WAYPOINTS_FILE):
        return {}
    try:
        with open(WAYPOINTS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}
