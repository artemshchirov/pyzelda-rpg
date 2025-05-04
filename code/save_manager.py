import json
import os

def save_game(data, filepath='savegame.json'):
    """Save the game state to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_game(filepath='savegame.json'):
    """Load the game state from a JSON file. Returns None if not found or error."""
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception:
        return None
