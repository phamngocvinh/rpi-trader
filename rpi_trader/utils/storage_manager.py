import json
import os
from config import STATE_FILE

def load_state(key, default_value=None):
    """
    Loads a specific value by key from the global state file (state.json).
    Returns the value, or default_value if the key/file is not found.
    """
    if not os.path.exists(STATE_FILE):
        return default_value
    
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            return state.get(key, default_value)
    except json.JSONDecodeError:
        # Handle case where file is empty or corrupted JSON
        print(f"Warning: {STATE_FILE} file corrupted or empty. Returning default value.")
        return default_value
    except Exception as e:
        print(f"Error loading state from {STATE_FILE}: {e}")
        return default_value

def save_state(key, value):
    """
    Saves a key-value pair to the global state file (state.json).
    """
    state = {}
    
    # 1. Load existing state first
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # If corrupted or empty, start with an empty state
            state = {}
        except Exception as e:
            print(f"Error loading state before saving: {e}")
            return False

    # 2. Update the specific key
    state[key] = value

    # 3. Write back the updated state
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving state to {STATE_FILE}: {e}")
        return False